import asyncio
import os
import time

import orjson

from api.aiotieba_client import get_posts
from config.path_config import ScrapeDataPathBuilder
from container.container import Container
from pojo.scraper_info import ScraperInfo
from services.post_service import PostService
from services.thread_service import ThreadService
from services.user_service import UserService
from utils.logger import generate_scrape_logger_msg
from utils.msg_printer import MsgPrinter


async def scrape(tid: int):
    scrape_start_time = time.time()

    pre_post = await get_posts(tid, 1)
    if pre_post is None:
        MsgPrinter.print_tip(
            "\n".join(["\n预加载错误，可能是以下原因:",
                       "1. 网络故障，请检查网络。",
                       "2. tid 错误, 请检查是否输入正确",
                       "3. 帖子可能已被删除", ]),
        )
        return

    # 预加载通过, 确认帖子已经存在
    scrape_data_path_builder = ScrapeDataPathBuilder(
        pre_post.forum.fname, tid, pre_post.thread.title
    )
    Container.set_scrape_data_path_builder(scrape_data_path_builder)

    # ScraperInfo
    with open(
            scrape_data_path_builder.get_scrape_info_path(), "w", encoding="utf-8"
    ) as file:
        file.write(orjson.dumps(ScraperInfo(tid)).decode("utf-8"))

    scraping_tid: int = tid
    while scraping_tid != 0:
        os.makedirs(
            scrape_data_path_builder.get_thread_dir(scraping_tid), exist_ok=True
        )

        Container.set_tid(scraping_tid)
        content_db = Container.get_content_db()
        scrape_logger = Container.get_scrape_logger()

        MsgPrinter.print_step_mark("开始爬取帖子", ["tid", scraping_tid])
        scrape_logger.info(generate_scrape_logger_msg("开始爬取帖子", "StepMark", ["tid", scraping_tid]))

        # posts 和 comments
        post_service = PostService()
        await post_service.scrape_post()

        thread_servie = ThreadService()
        forum_info = post_service.get_forum_info()
        thread_info = post_service.get_thread_info()

        # 集中完善用户数据
        MsgPrinter.print_step_mark("正在集中完善用户数据, 和爬取主题帖信息", ["tid", scraping_tid])
        scrape_logger.info(
            generate_scrape_logger_msg("正在集中完善用户数据, 和爬取主题帖信息", "StepMark", ["tid", scraping_tid]))
        user_service = UserService()
        await asyncio.gather(
            thread_servie.save_forum_info(forum_info.fid),
            thread_servie.save_thread_info(thread_info),
            user_service.complete_user_info()
        )

        content_db.close()

        MsgPrinter.print_step_mark("帖子爬取完成", ["tid", scraping_tid])
        scrape_logger.info(generate_scrape_logger_msg("帖子爬取完成", "StepMark", ["tid", scraping_tid]))

        scraping_tid = thread_info.share_origin.tid
        if scraping_tid != 0:
            MsgPrinter.print_step_mark(f"发现分享帖, 下面将爬取它的原帖")

    scrape_end_time = time.time()
    scrape_duration = scrape_end_time - scrape_start_time

    MsgPrinter.print_tip(f"全部爬取完成, 耗时 {scrape_duration // 60} 分 {round(scrape_duration % 60, 2)} 秒")
    MsgPrinter.print_tip(f"帖子数据保存在: {scrape_data_path_builder.get_item_dir()}")
