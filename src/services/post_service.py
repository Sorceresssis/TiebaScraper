import asyncio
import math

from aiotieba.typing import Posts, Comments, Post

from api.aiotieba_client import get_posts, get_comments
from container.container import Container
from db.post_dao import PostDao
from pojo.post_entity import PostEntity
from pojo.producer_consumer_contact import ProducerConsumerContact
from services.content_service import ContentService, ContentsAffiliation
from services.user_service import UserService
from utils.logger import generate_scrape_logger_msg
from utils.msg_printer import MsgPrinter


class PostService:
    def __init__(self):
        self.tid = Container.get_tid()
        self.scrape_logger = Container.get_scrape_logger()
        self.post_dao = PostDao()
        self.content_service = ContentService()
        self.user_service = UserService()
        self.update_threshold: int | None = None

    async def scrape_post(self, total_page: int, *, is_update: bool = False) -> None:
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

        latest_pid = 0
        if is_update:
            latest_post = self.post_dao.query_latest_post()
            if latest_post is not None:
                latest_pid = latest_post.id
            self.update_threshold = latest_pid

        for _ in range(consumers_num):
            tasks.append(self.save_post(contact, latest_pid))

        await asyncio.gather(*tasks)

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

    async def save_post(self, contact: ProducerConsumerContact, latest_pid: int = 0) -> None:
        while True:
            try:
                posts: Posts = await asyncio.wait_for(
                    contact.tasks_queue.get(), contact.consumer_await_timeout
                )

                if posts is None:
                    return

                for post in posts.objs:
                    try:
                        # Comment 1
                        # 已经被保存的帖子
                        if post.pid <= latest_pid:
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
                            )
                        )
                        MsgPrinter.print_success("", "SavePost", ["floor", post.floor, "pid", post.pid])

                        if len(post.comments) == 0:
                            continue

                        await self.scrape_comments(
                            post.pid,
                            post.floor,
                            posts.page.current_page,
                            post.reply_num,
                        )

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

        latest_sub_pid = 0
        if is_update:
            latest_sub_post = self.post_dao.query_latest_sub_post_by_pid(ppid)
            if latest_sub_post is not None:
                latest_sub_pid = self.post_dao.query_latest_sub_post_by_pid(ppid).id
                self.update_threshold = min(self.update_threshold, latest_sub_pid)

        await asyncio.gather(
            self.fetch_comments(contact, ppid, floor),
            *[self.save_comments(contact, ppn, latest_sub_pid) for _ in range(consumers_num)],
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

    async def save_comments(self, contact: ProducerConsumerContact, ppn: int, latest_sub_pid: int = 0):
        while True:
            try:
                comments: Comments = await asyncio.wait_for(
                    contact.tasks_queue.get(), contact.consumer_await_timeout
                )

                if comments is None:
                    return

                for comment in comments.objs:
                    try:
                        if comment.pid <= latest_sub_pid:
                            self.post_dao.update_post_traffic_by_id(
                                comment.pid, comment.agree, comment.disagree, 0
                            )
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
                            )
                        )

                        MsgPrinter.print_success(
                            "",
                            "SaveComment",
                            [
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
                            ],
                        )
                    except Exception as e:
                        MsgPrinter.print_error(
                            str(e),
                            "SaveComment",
                            [
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
                            ],
                        )
                        self.scrape_logger.error(
                            generate_scrape_logger_msg(
                                "保存失败",
                                "SaveComment",
                                [
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
                                ],
                            )
                        )
            except asyncio.TimeoutError:
                if contact.running_producers == 0:
                    return


# Comment 1 : 判断 pid 是否 <= 0 的注释。
# https://github.com/Starry-OvO/aiotieba/issues/210 已解决
"""
之所以要判断pid是否大于0, 是因为封装后的get_posts。请求到的数据可能会出现一个 pid=0, floor=0 的奇怪数据

实例:
tid = 8695394788
pn = 1
rn = 30

直接用 aiotieba 请求的结果是正确的
    代码:
        async with aiotieba.Client() as client:
            posts1 = await client.get_posts(tid, pn, rn=rn, with_comments=False)
            for post in posts1.objs:
                print(get_pid_floor(post))

    结果:
        ...省略...
        ---------------------------
        pid: 148955736398
        floor: 5
        content[0]: {"text":"兵长"}
         ---------------------------
        pid: 148955743416
        floor: 6
        content[0]: {"text":"莱纳"}
        ...省略...


调用封装后的 from .et.aiotieba_client import get_posts。请求到的数据会出现 pid=0 的多余数据
    代码:
        posts2 = await get_posts(tid, pn, rn)
        for post in posts1.objs:
            print(get_pid_floor(post))

    结果:
        ...省略...
        ---------------------------
        pid: 148955736398
        floor: 5
        content[0]: {"text":"兵长"}
        ---------------------------
        pid: 0
        floor: 0
        content[0]: {"text":"我们每个人打从出生开始就是自由的。"}
        ---------------------------
        pid: 148955743416
        floor: 6
        content[0]: {"text":"莱纳"}
        ...省略...
"""
