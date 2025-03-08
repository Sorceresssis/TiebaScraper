import asyncio
import os
import time

import orjson
import questionary

import src.config.scraper_config as scraper_config
from ..api.aiotieba_client import get_posts
from ..config.path_config import ScrapeDataPathBuilder
from ..container.container import Container
from ..pojo.scrape_info import ScrapeInfoDict, ScrapeRecordDict
from ..scrape_config import ScrapeConfig, ScrapeConfigKeys
from ..services.post_service import PostService
from ..services.thread_service import ThreadService
from ..services.user_service import UserService
from ..utils.cli_questionary import WarningStyle
from ..utils.common import json_dumps
from ..utils.logger import generate_scrape_logger_msg
from ..utils.msg_printer import MsgPrinter


async def scrape_update(path: str):
    if not os.path.isdir(path):
        MsgPrinter.print_error(
            "输入的路径不存在",
            "ScrapeUpdate",
        )
        return

    MsgPrinter.print_step_mark("开始读取本地数据")
    update_start_time = time.time()
    Container.set_scrape_timestamp(int(update_start_time))

    scrape_data_path_builder = ScrapeDataPathBuilder.get_instance_scrape_update(path)
    Container.set_scrape_data_path_builder(scrape_data_path_builder)

    # ANCHOR scrape_info.json
    scrape_info_path = scrape_data_path_builder.get_scrape_info_path()
    if not os.path.isfile(scrape_info_path):
        MsgPrinter.print_error(
            "未找到文件'scrape_info.json'",
            "ScrapeUpdate",
        )
        return

    with open(scrape_info_path, "r", encoding="utf-8") as file:
        scrape_info: ScrapeInfoDict = orjson.loads(file.read())

    new_scrape_record: ScrapeRecordDict = {
        "scrape_time": Container.get_scrape_timestamp(),
        "scrape_config": ScrapeConfig.to_dict(),
    }
    if "scrape_records" in scrape_info and len(scrape_info["scrape_records"]) > 0:
        scrape_records = scrape_info["scrape_records"]
        if not (
                await confirm_config(scrape_records[-1]["scrape_config"], new_scrape_record["scrape_config"])
        ):
            return

        scrape_info["scrape_records"].append(new_scrape_record)
    else:
        scrape_info["scrape_records"] = [new_scrape_record]

    scrape_info["update_time"] = Container.get_scrape_timestamp()
    scrape_info["scraper_version"] = scraper_config.SCRAPER_VERSION
    with open(scrape_info_path, "w", encoding="utf-8") as file:
        file.write(json_dumps(scrape_info))

    # ANCHOR main_thread
    main_thread_id = scrape_info["main_thread"]
    await update_thread(main_thread_id)

    with open(scrape_data_path_builder.get_thread_info_path(main_thread_id), "r", encoding="utf-8") as file:
        main_thread_info_dict = orjson.loads(file.read())

    # ANCHOR share_origin
    share_origin_id = main_thread_info_dict["share_origin"]
    if share_origin_id != 0:
        MsgPrinter.print_step_mark("开始处理 share_origin")
        await update_thread(share_origin_id, is_share_origin=True)

    update_end_time = time.time()
    update_duration = update_end_time - update_start_time
    MsgPrinter.print_step_mark("任务完成.")
    MsgPrinter.print_tip(f"耗时 {int(update_duration // 60)} 分 {round(update_duration % 60, 2)} 秒.")


async def update_thread(tid: int, *, is_share_origin=False):
    if tid <= 0:
        return

    Container.set_tid(tid)
    content_db = Container.get_content_db()
    scrape_logger = Container.get_scrape_logger()

    def final_treatment():
        content_db.close()

    # 在这里判断的原因是为了更新 share_origin 数据库的数据结构。
    if is_share_origin and (not ScrapeConfig.UPDATE_SHARE_ORIGIN):
        final_treatment()

    scrape_logger.info(generate_scrape_logger_msg("开始更新帖子", "StepMark", ["tid", tid]))

    pre_fetch_posts = await get_posts(tid)
    if pre_fetch_posts is None:
        final_treatment()
        MsgPrinter.print_error(f"帖子可能已删除", "ScrapeUpdate", ["tid", tid])
        scrape_logger.error(generate_scrape_logger_msg("帖子可能已删除", "ScrapeUpdate", ["tid", tid]))
        return

    post_service = PostService()
    user_service = UserService()
    thread_service = ThreadService()

    MsgPrinter.print_step_mark("开始更新 forum, thread 元信息", ["tid", tid])
    await asyncio.gather(
        thread_service.save_forum_info(pre_fetch_posts.forum.fid),
        thread_service.save_thread_info(pre_fetch_posts.thread),
    )

    MsgPrinter.print_step_mark("开始更新 posts", ["tid", tid])
    await post_service.scrape_post(pre_fetch_posts.page.total_page, is_update=True)

    MsgPrinter.print_step_mark("开始集中完善用户信息", ["tid", tid])
    scrape_logger.info(generate_scrape_logger_msg("正在集中完善用户数据", "StepMark", ["tid", tid]))
    await user_service.complete_user_info()

    final_treatment()
    MsgPrinter.print_step_mark("帖子更新完成", ["tid", tid])
    scrape_logger.info(generate_scrape_logger_msg("帖子更新完成", "StepMark", ["tid", tid]))


# 确认配置
async def confirm_config(old_config: dict, new_config: dict) -> bool:
    confirm_item = [
        (
            ScrapeConfigKeys.POST_FILTER_TYPE,
            "帖子过滤",
        ),
        (
            ScrapeConfigKeys.DOWNLOAD_USER_AVATAR_MODE,
            "用户头像下载模式",
        ),
    ]

    is_diff = False
    diff_msg = ""

    for item in confirm_item:
        if old_config[item[0]] != new_config[item[0]]:
            is_diff = True

            diff_msg += f"{item[1]}: {old_config[item[0]]} -> {new_config[item[0]]}\n"

    if is_diff:
        print(diff_msg)
        return await questionary.confirm(
            "本次爬取的配置与上一次爬取的配置存在差异，是否继续？", style=WarningStyle
        ).ask_async()
    else:
        return True
