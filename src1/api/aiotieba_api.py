import functools

import aiotieba as tb
import aiotieba.logging

# from scrape_config import ScrapeConfig, PostFilterType
# from tieba_auth import TiebaAuth
# from utils.msg_printer import MsgPrinter


bduss = ""


def retry(retries: int = 3):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                result = await func(*args, **kwargs)
                if result is None:
                    #     MsgPrinter.print_error(
                    #         f"第 {failures}/{retry} 次请求失败", "FetchForum", ["fname_or_fid", fname_or_fid]
                    #     )
                    print("失败")
                    attempt += 1
                else:
                    return result
            return None

        return wrapper

    return decorator


@retry(3)
async def get_forum(fname_or_fid: str | int):
    async with tb.Client(bduss) as client:
        forum = await client.get_forum(fname_or_fid)

        if forum and forum.fid != 0:
            return forum
        else:
            return None


@retry(3)
async def get_posts():
    pass


@retry(3)
async def get_subposts():
    pass


# async def get_forum_detail(fname_or_fid: str | int, retry=3):
#     failures = 0
#     while failures < retry:
#         async with tb.Client(TiebaAuth.BDUSS) as client:
#             forum_detail = await client.get_forum_detail(fname_or_fid)
#             if forum_detail and forum_detail.fid != 0:
#                 return forum_detail
#             else:
#                 failures += 1
#                 MsgPrinter.print_error(
#                     f"第 {failures}/{retry} 次请求失败", "FetchForumDetail", ["fname_or_fid", fname_or_fid]
#                 )
#
#     return None
#
#
# async def get_posts(tid: int, pn=1, retry=4):
#     failures = 0
#     only_thread_author = False
#     if PostFilterType.AUTHOR_POSTS_WITH_SUBPOSTS == ScrapeConfig.POST_FILTER_TYPE:
#         only_thread_author = True
#     elif PostFilterType.AUTHOR_POSTS_WITH_AUTHOR_SUBPOSTS == ScrapeConfig.POST_FILTER_TYPE:
#         only_thread_author = True
#
#     while failures < retry:
#         async with tb.Client(TiebaAuth.BDUSS) as client:
#             posts = await client.get_posts(tid, pn, with_comments=True, only_thread_author=only_thread_author)
#             if posts and posts.thread.tid != 0:
#                 return posts
#             else:
#                 failures += 1
#                 MsgPrinter.print_error(
#                     f"第 {failures}/{retry} 次请求失败", "FetchPosts", ["tid", tid, "pn", pn]
#                 )
#
#     return None
#
#
# async def get_comments(tid: int, pid: int, floor: int, pn=1, retry=4):
#     failures = 0
#     while failures < retry:
#         async with tb.Client(TiebaAuth.BDUSS) as client:
#             comments = await client.get_comments(tid, pid, pn)
#             if comments and comments.post.pid != 0:
#                 return comments
#             else:
#                 failures += 1
#                 MsgPrinter.print_error(
#                     f"第 {failures}/{retry} 次请求失败",
#                     "FetchComments",
#                     ["tid", tid, "floor", floor, "pid", pid, "pn", pn],
#                 )
#
#     return None
#
#
# async def get_user_info(user_id: str | int, portrait: str | None, retry=3):
#     """
#     获取用户信息
#     Args:
#         portrait:
#         user_id: 推荐 id 和 portrait 因为这两个参数是一定有的。
#         retry:
#
#     Returns:
#
#     """
#     failures = 0
#     while failures < retry:
#         async with tb.Client(TiebaAuth.BDUSS) as client:
#             user_info = await client.get_user_info(user_id)
#             if user_info and user_info.user_id != 0:
#                 return user_info
#             else:
#                 failures += 1
#                 MsgPrinter.print_error(
#                     f"第 {failures}/{retry} 次请求失败",
#                     "FetchUserInfo",
#                     ["user_id", user_id, "portrait", portrait],
#                 )
#
#     return None


import asyncio


async def main():
    await  get_forum("pythoan")

asyncio.run(main())