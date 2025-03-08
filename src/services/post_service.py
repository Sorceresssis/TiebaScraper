import asyncio
import math

from aiotieba.typing import Posts, Comments, Post

from ..api.aiotieba_client import get_posts, get_comments
from ..config.scraper_config import SCRAPER_VERSION
from ..container.container import Container
from ..db.post_dao import PostDao
from ..db.scrape_batch_dao import ScrapeBatchDao
from ..db.tieba_origin_src_dao import TiebaOriginSrcDao
from ..db.user_dao import UserDao
from ..pojo.post_entity import PostEntity
from ..pojo.producer_consumer_contact import ProducerConsumerContact
from ..scrape_config import PostFilterType, ScrapeConfig
from ..services.content_service import ContentService, ContentsAffiliation
from ..services.user_service import UserService
from ..utils.common import json_dumps
from ..utils.fs import delete_matching_files
from ..utils.logger import generate_scrape_logger_msg
from ..utils.msg_printer import MsgPrinter


class PostService:
    def __init__(self):
        self.scrape_data_path_builder = Container.get_scrape_data_path_builder()
        self.tid = Container.get_tid()
        self.scrape_batch_id = 0
        self.scrape_logger = Container.get_scrape_logger()
        self.post_dao = PostDao()
        self.user_dao = UserDao()
        self.tieba_origin_src_dao = TiebaOriginSrcDao()
        self.scrape_batch_dao = ScrapeBatchDao()
        self.content_service = ContentService()
        self.user_service = UserService()

    async def scrape_post(self, total_page: int, *, is_update: bool = False) -> None:
        self.scrape_batch_id = self.scrape_batch_dao.insert(
            SCRAPER_VERSION, json_dumps(ScrapeConfig.to_dict(), False), Container.get_scrape_timestamp()
        )

        queue_maxsize = 10
        max_producers_num = 3
        producers_num = min(max_producers_num, total_page)
        consumers_num = 8
        consumer_await_timeout = 8
        contact = ProducerConsumerContact(queue_maxsize, producers_num, consumers_num, consumer_await_timeout)

        pages_per_producer = math.ceil(total_page / producers_num)

        tasks = []
        start_pn = 1
        for i in range(producers_num):
            end_pn = start_pn + pages_per_producer - 1
            if i == producers_num - 1:
                end_pn = total_page
            tasks.append(self.fetch_post(contact, start_pn, end_pn))
            start_pn = end_pn + 1

        for _ in range(consumers_num):
            tasks.append(self.save_post(contact, is_update))

        await asyncio.gather(*tasks)

        if (
            PostFilterType.AUTHOR_AND_REPLIED_POSTS_WITH_SUBPOSTS == ScrapeConfig.POST_FILTER_TYPE
            or PostFilterType.AUTHOR_AND_REPLIED_POSTS_WITH_AUTHOR_SUBPOSTS == ScrapeConfig.POST_FILTER_TYPE
        ):
            self.user_dao.delete_user_without_post()

    async def fetch_post(
        self,
        contact: ProducerConsumerContact,
        start_pn: int,
        end_pn: int,
    ) -> None:
        pn = start_pn

        while pn <= end_pn:
            posts = await get_posts(self.tid, pn)
            pn += 1
            if posts is None:
                self.scrape_logger.error(generate_scrape_logger_msg("请求失败", "FetchPosts", ["pn", pn]))
                continue

            await contact.tasks_queue.put(posts)

        contact.running_producers -= 1
        if contact.running_producers == 0:
            for _ in range(contact.consumers_num):
                await contact.tasks_queue.put(None)

    async def save_post(self, contact: ProducerConsumerContact, is_update: bool = False) -> None:
        while True:
            try:
                posts: Posts = await asyncio.wait_for(
                    contact.tasks_queue.get(), contact.consumer_await_timeout
                )

                if posts is None:
                    return

                for post in posts.objs:
                    try:
                        # https://github.com/Starry-OvO/aiotieba/issues/210
                        if post.pid <= 0:
                            continue

                        # 已经被保存的帖子
                        if is_update and self.post_dao.is_existing_post(post.pid):
                            self.post_dao.update_post_traffic_by_id(
                                post.pid, post.agree, post.disagree, post.reply_num
                            )

                            if len(post.comments) != 0:
                                await self.scrape_comments(
                                    post.pid,
                                    post.floor,
                                    posts.page.current_page,
                                    post.reply_num,
                                    is_update=True,
                                )
                            continue

                        if (
                            PostFilterType.AUTHOR_POSTS_WITH_SUBPOSTS == ScrapeConfig.POST_FILTER_TYPE
                            or PostFilterType.AUTHOR_POSTS_WITH_AUTHOR_SUBPOSTS
                            == ScrapeConfig.POST_FILTER_TYPE
                        ) and (not post.is_thread_author):
                            continue

                        await self.user_service.register_user_from_post_user(post.user)
                        post_contents = await self.content_service.process_contents(
                            post.contents.objs,
                            ContentsAffiliation(posts.page.current_page, post.pid, post.floor),
                        )
                        self.post_dao.insert(
                            PostEntity(
                                post.pid,
                                post_contents,
                                post.floor,
                                post.author_id,
                                post.agree,
                                post.disagree,
                                post.create_time,
                                post.is_thread_author,
                                post.sign,
                                post.reply_num,
                                0,
                                0,
                                self.scrape_batch_id,
                            )
                        )
                        MsgPrinter.print_success("", "SavePost", ["floor", post.floor, "pid", post.pid])

                        if len(post.comments) > 0:
                            await self.scrape_comments(
                                post.pid,
                                post.floor,
                                posts.page.current_page,
                                post.reply_num,
                            )

                        # AUTHOR_AND_REPLIED_POSTS_WITH_XXXXX 处理
                        if (not post.is_thread_author) and (
                            PostFilterType.AUTHOR_AND_REPLIED_POSTS_WITH_SUBPOSTS
                            == ScrapeConfig.POST_FILTER_TYPE
                            or PostFilterType.AUTHOR_AND_REPLIED_POSTS_WITH_AUTHOR_SUBPOSTS
                            == ScrapeConfig.POST_FILTER_TYPE
                        ):
                            # len(post.comments) == 0 减少数据库查询
                            if len(post.comments) == 0 or (
                                not self.post_dao.is_author_replied_post(post.pid, self.scrape_batch_id)
                            ):
                                self.post_dao.delete(post.pid)
                                await self.delete_post_assets(post.pid)

                                subposts_cursor = self.post_dao.query_subposts_by_pid_and_batch_id(
                                    post.pid, self.scrape_batch_id
                                )
                                while row := subposts_cursor.fetchone():
                                    if row is None:
                                        break
                                    self.post_dao.delete(row[0])
                                    await self.delete_post_assets(row[0])

                            # NOTE
                            # 问: 为什么本程序不把 post_assets、user_avatar 这些需要下载的资源，先记录到数据库, 到最后再集中下载呢。
                            # 到最后集中下载, 就可以免去 AUTHOR_AND_REPLIED_POSTS_WITH_XXXXX 对 文件的删除。
                            # 答: 因为我无法得知文件的后缀名, 文件的下载依靠的是 http 的 content_type 表头。
                            # 虽然目前的图片、视频、音频的格式是固定的。但是如果以后出现了新的格式, 那么程序就很难修改。

                    except Exception as e:
                        MsgPrinter.print_error(
                            str(e),
                            "SavePost",
                            [
                                "floor",
                                post.floor,
                                "pid",
                                post.pid,
                                "pn",
                                posts.page.current_page,
                            ],
                        )
                        self.scrape_logger.error(
                            generate_scrape_logger_msg(
                                str(e),
                                "SavePost",
                                [
                                    "floor",
                                    post.floor,
                                    "pid",
                                    post.pid,
                                    "pn",
                                    posts.page.current_page,
                                ],
                            )
                        )
            except asyncio.TimeoutError:
                if contact.running_producers == 0:
                    return

    async def delete_post_assets(self, pid: int) -> None:
        filename_pattern = self.scrape_data_path_builder.get_post_assets_filename_pattern(pid)
        deleted_files = await delete_matching_files(
            self.scrape_data_path_builder.get_post_assets_dir(self.tid), filename_pattern
        )

        for file in deleted_files:
            self.tieba_origin_src_dao.delete_by_filename(file)

    async def save_post_from_floor1(self, post: Post):
        if post.pid <= 0:
            return

        await self.user_service.register_user_from_post_user(post.user)

        post_contents = await self.content_service.process_contents(
            post.contents.objs,
            ContentsAffiliation(),
        )
        self.post_dao.insert(
            PostEntity(
                post.pid,
                post_contents,
                post.floor,
                post.author_id,
                post.agree,
                post.disagree,
                post.create_time,
                post.is_thread_author,
                post.sign,
                post.reply_num,
                0,
                0,
                self.scrape_batch_id,
            )
        )
        MsgPrinter.print_success("", "SavePost", ["floor", post.floor, "pid", post.pid])

    async def scrape_comments(
        self,
        ppid: int,
        floor: int,
        ppn: int,
        reply_num: int,
        *,
        is_update: bool = False,
    ) -> None:
        queue_maxsize = 8 if reply_num > 8 else reply_num
        producers_num = 1
        consumers_num = queue_maxsize
        consumer_await_timeout = 8
        contact = ProducerConsumerContact(queue_maxsize, producers_num, consumers_num, consumer_await_timeout)

        await asyncio.gather(
            self.fetch_comments(contact, ppid, floor),
            *[self.save_comments(contact, ppn, is_update) for _ in range(consumers_num)],
        )

    async def fetch_comments(self, contact: ProducerConsumerContact, ppid: int, floor: int):
        pn = 1
        total_page = pn

        while total_page >= pn:
            comments = await get_comments(self.tid, ppid, floor, pn)
            pn += 1
            if comments is None:
                self.scrape_logger.error(
                    generate_scrape_logger_msg(
                        "请求失败",
                        "FetchComments",
                        ["floor", floor, "ppid", ppid, "pn", pn],
                    )
                )
                continue

            await contact.tasks_queue.put(comments)

            new_total_page = comments.page.total_page
            if new_total_page > total_page:
                total_page = new_total_page

        contact.running_producers -= 1
        if contact.running_producers == 0:
            for _ in range(contact.consumers_num):
                await contact.tasks_queue.put(None)

    async def save_comments(self, contact: ProducerConsumerContact, ppn: int, is_update: bool = False):
        while True:
            try:
                comments: Comments = await asyncio.wait_for(
                    contact.tasks_queue.get(), contact.consumer_await_timeout
                )

                if comments is None:
                    return

                for comment in comments.objs:
                    comment_affiliations = [
                        "floor",
                        comment.floor,
                        "pid",
                        comment.pid,
                        "pn",
                        comments.page.current_page,
                        "ppid",
                        comment.ppid,
                        "ppn",
                        ppn,
                    ]

                    try:
                        # 更新要在过滤前面。
                        if is_update and self.post_dao.is_existing_post(comment.pid):
                            self.post_dao.update_post_traffic_by_id(
                                comment.pid, comment.agree, comment.disagree, 0
                            )
                            continue

                        if (
                            PostFilterType.AUTHOR_POSTS_WITH_AUTHOR_SUBPOSTS == ScrapeConfig.POST_FILTER_TYPE
                            or PostFilterType.AUTHOR_POSTS_WITH_AUTHOR_SUBPOSTS
                            == ScrapeConfig.POST_FILTER_TYPE
                        ) and (not comment.is_thread_author):
                            continue

                        await self.user_service.register_user_from_comment_user(comment.user)
                        # 之前想被回复者一定回出现在楼中楼里，所以没有去把回复者插入数据
                        # 但是可能回出现被回复在删除自己回复的情况所以这里也要执行insert操作
                        if comment.reply_to_id != 0:
                            await self.user_service.register_user_from_id(comment.reply_to_id)

                        comment_contents = await self.content_service.process_contents(
                            comment.contents.objs,
                            ContentsAffiliation(
                                ppn,
                                comment.ppid,
                                comment.floor,
                                comments.page.current_page,
                                comment.pid,
                            ),
                        )

                        self.post_dao.insert(
                            PostEntity(
                                comment.pid,
                                comment_contents,
                                comment.floor,
                                comment.author_id,
                                comment.agree,
                                comment.disagree,
                                comment.create_time,
                                comment.is_thread_author,
                                "",
                                0,
                                comment.ppid,
                                comment.reply_to_id,
                                self.scrape_batch_id,
                            )
                        )

                        MsgPrinter.print_success(
                            "",
                            "SaveComment",
                            comment_affiliations,
                        )
                    except Exception as e:
                        MsgPrinter.print_error(
                            str(e),
                            "SaveComment",
                            comment_affiliations,
                        )
                        self.scrape_logger.error(
                            generate_scrape_logger_msg(
                                "保存失败",
                                "SaveComment",
                                comment_affiliations,
                            )
                        )
            except asyncio.TimeoutError:
                if contact.running_producers == 0:
                    return
