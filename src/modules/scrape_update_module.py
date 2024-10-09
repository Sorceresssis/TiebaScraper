import asyncio
import os
import time

import orjson

from api.aiotieba_client import get_posts
from config.path_config import ScrapeDataPathBuilder
from container.container import Container
from pojo.scraper_info import ScraperInfoDict
from services.post_service import PostService
from services.thread_service import ThreadService
from services.user_service import UserService
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

    data: ScraperInfoDict
    with open(scrape_info_path, "r") as file:
        data = orjson.loads(file.read())

    updating_tid = data["main_thread"]
    while updating_tid != 0:
        Container.set_tid(updating_tid)
        content_db = Container.get_content_db()
        scrape_logger = Container.get_scrape_logger()

        with open(scrape_data_path_builder.get_thread_info_path(updating_tid), "r") as file:
            thread_info_dict = orjson.loads(file.read())

        pre_fetch_posts = await get_posts(updating_tid)

        if pre_fetch_posts is None:
            MsgPrinter.print_error(f"帖子可能已删除", "ScrapeUpdate", ["tid", updating_tid])
            updating_tid = thread_info_dict["share_origin"]
            continue

        post_service = PostService()
        user_service = UserService()
        thread_service = ThreadService()

        await post_service.scrape_post(pre_fetch_posts.page.total_page, is_update=True)

        MsgPrinter.print_step_mark()
        await asyncio.gather(
            thread_service.save_forum_info(pre_fetch_posts.forum.fid),
            thread_service.save_thread_info(pre_fetch_posts.thread),
        )

        MsgPrinter.print_step_mark("开始集中完善用户信息", ["tid", updating_tid])

        # TODO update shared origin config

        content_db.close()
        MsgPrinter.print_step_mark("帖子更新完成", ["tid", updating_tid])

        updating_tid = thread_info_dict["share_origin"]

    data["update_times"].append(Container.get_scrape_timestamp())
    with open(scrape_info_path, "w") as file:
        file.write(orjson.dumps(data).decode("utf-8"))

    update_end_time = time.time()
    update_duration = update_end_time - update_start_time

    MsgPrinter.print_step_mark("任务完成.")
    MsgPrinter.print_tip(f"耗时 {int(update_duration // 60)} 分 {round(update_duration % 60, 2)} 秒.")
