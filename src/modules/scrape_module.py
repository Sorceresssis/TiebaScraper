import asyncio
import os
import time

from aiotieba.api.get_posts._classdef import ShareThread_pt

from api.aiotieba_client import get_posts
from config.path_config import ScrapeDataPathBuilder
from container.container import Container
from pojo.scrape_info import ScrapeInfo
from scrape_config import ScrapeConfig
from services.post_service import PostService
from services.thread_service import ThreadService
from services.user_service import UserService
from utils.common import counter_gen, json_dumps
from utils.logger import generate_scrape_logger_msg
from utils.msg_printer import MsgPrinter

counter = counter_gen()
next(counter)


async def scrape(tid: int):
    scrape_start_time = time.time()
    Container.set_scrape_timestamp(int(scrape_start_time))

    pre_post = await get_posts(tid, 1)
    if pre_post is None:
        counter.send((0, 1))
        MsgPrinter.print_tip(
            "\n".join(
                [
                    "\n预加载错误，可能是以下原因:",
                    f"{next(counter)}. 连接错误，请多尝试几次。",
                    f"{next(counter)}. 网络故障，请检查网络。",
                    f"{next(counter)}. tid 错误, 请检查是否输入正确",
                    f"{next(counter)}. 帖子可能已被屏蔽或删除",
                    f"{next(counter)}. BDUSS 失效，请重新配置",
                ]
            ),
        )
        return

    scrape_data_path_builder = ScrapeDataPathBuilder.get_instance_scrape(
        pre_post.forum.fname, tid, pre_post.thread.title
    )
    Container.set_scrape_data_path_builder(scrape_data_path_builder)

    with open(scrape_data_path_builder.get_scrape_info_path(), "w", encoding="utf-8") as file:
        file.write(
            json_dumps(
                ScrapeInfo(
                    tid,
                    Container.get_scrape_timestamp(),
                    {
                        "scrape_time": Container.get_scrape_timestamp(),
                        "scrape_config": ScrapeConfig.to_dict(),
                    },
                )
            )
        )

    main_thread_id = tid
    await scrape_thread(main_thread_id)

    share_origin_id = pre_post.thread.share_origin.tid
    if share_origin_id != 0:
        MsgPrinter.print_step_mark("开始处理 share_origin")
        await scrape_thread(share_origin_id, is_share_origin=True, share_origin=pre_post.thread.share_origin)

    scrape_end_time = time.time()
    scrape_duration = scrape_end_time - scrape_start_time

    MsgPrinter.print_step_mark("任务完成")
    MsgPrinter.print_tip(f"耗时 {int(scrape_duration // 60)} 分 {round(scrape_duration % 60, 2)} 秒")
    MsgPrinter.print_tip(f"帖子数据保存在: {scrape_data_path_builder.get_item_dir()}")


async def scrape_thread(tid: int, *, is_share_origin: bool = False, share_origin: ShareThread_pt | None = None):
    if tid <= 0:
        return

    Container.set_tid(tid)
    scrape_data_path_builder = Container.get_scrape_data_path_builder()
    os.makedirs(scrape_data_path_builder.get_thread_dir(tid), exist_ok=True)
    content_db = Container.get_content_db()
    scrape_logger = Container.get_scrape_logger()

    def final_treatment():
        content_db.close()

    MsgPrinter.print_step_mark("开始爬取帖子", ["tid", tid])
    scrape_logger.info(generate_scrape_logger_msg("开始爬取帖子", "StepMark", ["tid", tid]))

    pre_fetch_posts = await get_posts(tid)

    thread_service = ThreadService()
    user_service = UserService()
    post_service = PostService()

    if pre_fetch_posts is None:
        if is_share_origin and (share_origin is not None):
            MsgPrinter.print_step_mark(f"share_origin 可能已被屏蔽或删除, 开始尽可能的保存数据", ["tid", tid])
            await asyncio.gather(
                thread_service.save_forum_info(share_origin.fid),
                thread_service.save_thread_from_share_origin(share_origin),
                user_service.register_user_from_id(share_origin.author_id),
                user_service.complete_user_info(),
            )
        final_treatment()
        return

    await asyncio.gather(
        thread_service.save_forum_info(pre_fetch_posts.forum.fid),
        thread_service.save_thread_info(pre_fetch_posts.thread),
    )

    if is_share_origin and (not ScrapeConfig.SCRAPE_SHARE_ORIGIN):
        # 如果不爬取源，就只保存原帖的 第一楼。
        MsgPrinter.print_tip(
            "当前配置为不保存 share_origin, 下面只保存 share_origin 的第一楼.",
            ["tid", tid],
        )
        await post_service.save_post_from_floor1(pre_fetch_posts.objs[0])

        final_treatment()
        return

    await post_service.scrape_post(pre_fetch_posts.page.total_page)

    MsgPrinter.print_step_mark("正在集中完善用户数据", ["tid", tid])
    scrape_logger.info(generate_scrape_logger_msg("正在集中完善用户数据", "StepMark", ["tid", tid]))
    await user_service.complete_user_info()

    final_treatment()
    MsgPrinter.print_step_mark("帖子爬取完成", ["tid", tid])
    scrape_logger.info(generate_scrape_logger_msg("帖子爬取完成", "StepMark", ["tid", tid]))
