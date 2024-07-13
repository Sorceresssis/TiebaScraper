import orjson
from net.aiotieba_client import get_posts, get_comments
from aiotieba.api.get_posts import Posts, Post
from aiotieba.api.get_comments import Comment
from container import Container
from pojo.thread_info import ThreadInfo, VoteInfo, VoteOptoin
from entity.post_entity import PostEntity
from dao.post_dao import PostDao
from services.forum_service import ForumService
from services.user_service import UserService
from services.content_service import ContentService


class ThreadService:
    def __init__(self):
        self.share_origin = 0
        self.tid = Container.get_tid()
        self.scraped_path_constructor = Container.get_scraped_path_constructor()
        self.user_service = UserService()
        self.content_service = ContentService()
        self.post_dao = PostDao()
        self.scrape_logger = Container.get_scrape_logger()

    async def scrape(self) -> None:
        msg = f"开始爬取帖子: {self.tid}"
        print(msg)
        self.scrape_logger.info(msg)

        # 遍历帖子
        posts_pn = 1
        posts_total_page = posts_pn
        failures = 0
        saved_thread_info = False
        while posts_total_page >= posts_pn:
            Container.set_current_posts_pn(posts_pn)
            posts = await get_posts(self.tid, posts_pn)
            # 有时候网络请求会失败，继续爬取当前页
            if posts or failures > 2:
                posts_pn += 1
                failures = 0
            else:
                failures += 1
                e_msg = f"第{posts_pn}页请求失败,开始第{failures}次重试"
                print(e_msg)
                self.scrape_logger.error(e_msg)
                continue

            if (not saved_thread_info) and posts:
                saved_thread_info = True
                # 查看是否有分享帖
                self.share_origin = posts.thread.share_origin.tid

                forum_service = ForumService(posts.forum.fid)
                await forum_service.save_forum_info()

                # 保存主题信息
                self.save_thread_info(posts)

            # 保存帖子内容和用户
            for post in posts.objs:
                # 请求的数据会出现 pid 重复的情况。会触发pid的UniqueConstraintError
                try:
                    # 这里判断 pid 是否 <= 0 注释，见本文件最下方 # Comment 1
                    if post.pid <= 0:
                        continue
                    await self.save_post(post)
                except Exception as e:
                    e_msg = f"保存帖子失败: pid:{post.pid}, floor:{post.floor}, {e}"
                    print(e_msg)
                    self.scrape_logger.error(e_msg)

                # 爬取回复
                if len(post.comments) == 0:
                    continue

                comments_pn = 1
                comments_total_page = comments_pn
                comments_failures = 0
                while comments_total_page >= comments_pn:
                    comments = await get_comments(self.tid, post.pid, comments_pn)

                    if comments or comments_failures > 2:
                        comments_pn += 1
                        comments_failures = 0
                    else:
                        comments_failures += 1
                        e_msg = f"floor:{post.floor}。 第{comments_pn}页评论请求失败,开始第{comments_failures}次重试"
                        print(e_msg)
                        self.scrape_logger.error(e_msg)
                        continue

                    for comment in comments.objs:
                        try:
                            await self.save_comment(comment)
                        except Exception as e:
                            e_msg = f"保存评论失败: pid:{comment.pid}, floor:{comment.floor}, {e}"
                            print(e_msg)
                            self.scrape_logger.error(e_msg)

                    comments_total_page = (
                        comments.page.total_page
                        if comments.page.total_page > comments_total_page
                        else comments_total_page
                    )

            print(f"第{posts_pn - 1}页爬取完成, 共{posts.page.total_page}页。")

            # 部分帖子会出现某一页请求超出范围的问题，但实际上后面还有楼层，因此第一次请求的total_page是才是准确的。后续的 has_more 和 total_page 可能是错误的。
            posts_total_page = (
                posts.page.total_page
                if posts.page.total_page > posts_total_page
                else posts_total_page
            )

    def get_share_origin(self) -> int:
        return self.share_origin

    def save_thread_info(self, posts: Posts) -> None:
        forum_p = posts.forum
        thread_p = posts.thread

        thread_info = ThreadInfo(
            thread_p.tid,
            thread_p.title,
            forum_p.fid,
            posts.objs[0].pid,
            thread_p.author_id,
            thread_p.type,
            thread_p.is_share,
            thread_p.is_help,
            VoteInfo(
                thread_p.vote_info.title,
                thread_p.vote_info.is_multi,
                thread_p.vote_info.total_vote,
                thread_p.vote_info.total_user,
                list(
                    map(
                        lambda x: VoteOptoin(
                            x.text,
                            x.vote_num,
                        ),
                        thread_p.vote_info.options,
                    )
                ),
            ),
            thread_p.share_origin.tid,
            thread_p.view_num,
            thread_p.reply_num,
            thread_p.share_num,
            thread_p.agree,
            thread_p.disagree,
            thread_p.create_time,
        )

        with open(
            self.scraped_path_constructor.get_thread_info_path(self.tid),
            "w",
            encoding="utf-8",
        ) as file:
            file.write(orjson.dumps(thread_info).decode("utf-8"))

    async def save_post(self, post: Post):
        print(f"正在爬取第 {post.floor} 楼, pid = {post.pid}")
        # 爬取用户信息
        await self.user_service.save_user_info_by_uip(post.user)

        # 爬取帖子内容
        post_contents = await self.content_service.process_contents(
            post.pid, post.floor, post.contents.objs
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

    async def save_comment(self, comment: Comment):
        print(f"正在爬取楼中楼, pid = {comment.pid}")
        # 爬取用户信息
        await self.user_service.save_user_info_by_uic(comment.user)

        # 爬取回复内容
        comment_contents = await self.content_service.process_contents(
            comment.pid, comment.floor, comment.contents.objs
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
