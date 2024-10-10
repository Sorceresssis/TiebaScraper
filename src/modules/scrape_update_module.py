import asyncio
import os
import time

import orjson

import config.scraper_config as scraper_config
from api.aiotieba_client import get_posts
from config.path_config import ScrapeDataPathBuilder
from container.container import Container
from pojo.scraper_info import ScraperInfoDict
from scrape_config import ScrapeConfig
from services.post_service import PostService
from services.thread_service import ThreadService
from services.user_service import UserService
from utils.logger import generate_scrape_logger_msg
from utils.msg_printer import MsgPrinter


async def scrape_update(path: str):
    update_start_time = time.time()
    Container.set_scrape_timestamp(int(update_start_time))

    MsgPrinter.print_step_mark("开始读取本地数据")

    if not os.path.isdir(path):
        MsgPrinter.print_error(
            "输入的路径不存在",
            "ScrapeUpdate",
        )
        return

    scrape_data_path_builder = ScrapeDataPathBuilder.get_instance_scrape_update(path)
    Container.set_scrape_data_path_builder(scrape_data_path_builder)

    scrape_info_path = scrape_data_path_builder.get_scrape_info_path()
    if not os.path.isfile(scrape_info_path):
        MsgPrinter.print_error(
            "未找到文件'scrape_info.json'",
            "ScrapeUpdate",
        )
        return

    scraper_info: ScraperInfoDict
    with open(scrape_info_path, "r") as file:
        scraper_info = orjson.loads(file.read())

    updating_tid = scraper_info["main_thread"]
    is_updating_share_origin = False
    while updating_tid != 0:
        Container.set_tid(updating_tid)
        content_db = Container.get_content_db()

        if is_updating_share_origin:
            if ScrapeConfig.UPDATE_SHARE_ORIGIN:
                MsgPrinter.print_step_mark(f"开始更新原帖")
            else:
                break

        with open(scrape_data_path_builder.get_thread_info_path(updating_tid), "r") as file:
            thread_info_dict = orjson.loads(file.read())

        scrape_logger = Container.get_scrape_logger()
        scrape_logger.info(generate_scrape_logger_msg("开始更新帖子", "StepMark", ["tid", updating_tid]))

        pre_fetch_posts = await get_posts(updating_tid)

        if pre_fetch_posts is None:
            MsgPrinter.print_error(f"帖子可能已删除", "ScrapeUpdate", ["tid", updating_tid])
            scrape_logger.error(generate_scrape_logger_msg("帖子可能已删除", "ScrapeUpdate", ["tid", updating_tid]))

            updating_tid = thread_info_dict["share_origin"]
            if updating_tid != 0:
                is_updating_share_origin = True
            continue

        post_service = PostService()
        user_service = UserService()
        thread_service = ThreadService()

        await post_service.scrape_post(pre_fetch_posts.page.total_page, is_update=True)

        await asyncio.gather(
            thread_service.save_forum_info(pre_fetch_posts.forum.fid),
            thread_service.save_thread_info(pre_fetch_posts.thread),
        )

        MsgPrinter.print_step_mark("开始集中完善用户信息", ["tid", updating_tid])
        scrape_logger.info(generate_scrape_logger_msg("正在集中完善用户数据", "StepMark", ["tid", updating_tid]))
        await user_service.complete_user_info()

        content_db.close()
        MsgPrinter.print_step_mark("帖子更新完成", ["tid", updating_tid])
        scrape_logger.info(generate_scrape_logger_msg("帖子更新完成", "StepMark", ["tid", updating_tid]))

        updating_tid = thread_info_dict["share_origin"]
        if updating_tid != 0:
            is_updating_share_origin = True

    scraper_info["update_times"].append(Container.get_scrape_timestamp())
    scraper_info["scraper_version"] = scraper_config.SCRAPER_VERSION
    with open(scrape_info_path, "w") as file:
        file.write(orjson.dumps(scraper_info).decode("utf-8"))

    update_end_time = time.time()
    update_duration = update_end_time - update_start_time

    MsgPrinter.print_step_mark("任务完成.")
    MsgPrinter.print_tip(f"耗时 {int(update_duration // 60)} 分 {round(update_duration % 60, 2)} 秒.")
