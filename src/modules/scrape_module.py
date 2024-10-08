import asyncio
import os
import time

import orjson

from api.aiotieba_client import get_posts
from config.path_config import ScrapeDataPathBuilder
from container.container import Container
from pojo.scraper_info import ScraperInfo
from scrape_config import ScrapeConfig
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
            "\n".join(
                [
                    "\n预加载错误，可能是以下原因:",
                    "1. 连接错误，请多尝试几次。" "2. 网络故障，请检查网络。",
                    "3. tid 错误, 请检查是否输入正确",
                    "4. 帖子可能已被删除",
                    "5. BDUSS 失效，请重新配置",
                ]
            ),
        )
        return

    # 预加载通过, 确认帖子已经存在
    scrape_data_path_builder = ScrapeDataPathBuilder.get_instance_scrape(
        pre_post.forum.fname, tid, pre_post.thread.title
    )
    Container.set_scrape_data_path_builder(scrape_data_path_builder)

    # ScraperInfo
    with open(scrape_data_path_builder.get_scrape_info_path(), "w", encoding="utf-8") as file:
        file.write(orjson.dumps(ScraperInfo(tid)).decode("utf-8"))

    scraping_tid: int = tid
    is_scraping_share_origin: bool = False
    share_origin = None
    while scraping_tid != 0:
        os.makedirs(scrape_data_path_builder.get_thread_dir(scraping_tid), exist_ok=True)

        Container.set_tid(scraping_tid)
        content_db = Container.get_content_db()
        scrape_logger = Container.get_scrape_logger()

        MsgPrinter.print_step_mark("开始爬取帖子", ["tid", scraping_tid])
        scrape_logger.info(generate_scrape_logger_msg("开始爬取帖子", "StepMark", ["tid", scraping_tid]))

        posts = await get_posts(scraping_tid, 1)

        thread_service = ThreadService()
        user_service = UserService()
        post_service = PostService()

        if posts is None:
            if is_scraping_share_origin:
                MsgPrinter.print_step_mark(
                    f"由于原帖 {scraping_tid} 请求失败, 开始根据share_origin尽可能的保留数据"
                )
                # 如果是转发帖的原帖,错误，根据 main_thread 的 share_origin 里的信息尽可能的保留数据
                thread_servie = ThreadService()
                await asyncio.gather(
                    thread_servie.save_forum_info(share_origin.fid),
                    thread_servie.save_thread_from_share_origin(share_origin),
                    user_service.register_user_from_id(share_origin.author_id),
                    user_service.complete_user_info(),
                )
        else:
            # 保存帖子的元信息。
            forum_ps = posts.forum
            thread_ps = posts.thread

            # posts 和 comments
            if is_scraping_share_origin and (not ScrapeConfig.SCRAPE_SHARE_ORIGIN):
                # 如果不爬取原题，就只保存原帖的 第一楼。
                MsgPrinter.print_step_mark(
                    "当前配置为禁止保存转发原帖，所以只保存原帖的第一楼。",
                    ["tid", scraping_tid],
                )

                await asyncio.gather(
                    thread_service.save_forum_info(forum_ps.fid),
                    thread_service.save_thread_info(thread_ps),
                    post_service.save_post_from_floor1(posts.objs[0]),
                )
            else:
                await asyncio.gather(
                    thread_service.save_forum_info(forum_ps.fid),
                    thread_service.save_thread_info(thread_ps),
                    post_service.scrape_post(posts.page.total_page),
                )

            # 集中完善用户数据
            MsgPrinter.print_step_mark("正在集中完善用户数据", ["tid", scraping_tid])
            scrape_logger.info(
                generate_scrape_logger_msg("正在集中完善用户数据", "StepMark", ["tid", scraping_tid])
            )
            await user_service.complete_user_info()

        content_db.close()
        MsgPrinter.print_step_mark("帖子爬取完成", ["tid", scraping_tid])
        scrape_logger.info(generate_scrape_logger_msg("帖子爬取完成", "StepMark", ["tid", scraping_tid]))

        if posts is None:
            scraping_tid = 0
        else:
            scraping_tid = posts.thread.share_origin.tid
            share_origin = posts.thread.share_origin

        if scraping_tid != 0:
            is_scraping_share_origin = True
            MsgPrinter.print_step_mark(f"发现转发帖, 下面将爬取它的原帖{scraping_tid}")

    scrape_end_time = time.time()
    scrape_duration = scrape_end_time - scrape_start_time

    MsgPrinter.print_step_mark("任务完成")
    MsgPrinter.print_tip(f"耗时 {int(scrape_duration // 60)} 分 {round(scrape_duration % 60, 2)} 秒")
    MsgPrinter.print_tip(f"帖子数据保存在: {scrape_data_path_builder.get_item_dir()}")
