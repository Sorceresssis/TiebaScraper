import aiofiles
import orjson
from aiotieba.api.get_posts._classdef import Thread_p, ShareThread_pt

from api.aiotieba_client import get_forum, get_forum_detail
from container.container import Container
from db.tieba_origin_src_dao import TiebaOriginSrcDao
from pojo.content_frag import ContentFragType
from pojo.forum_info import ForumInfo
from pojo.thread_info import ThreadInfo, VoteInfo, VoteOption
from pojo.tieba_origin_src_entity import TiebaOriginSrcEntity
from utils.fs import download_file
from utils.logger import generate_scrape_logger_msg
from utils.msg_printer import MsgPrinter


class ThreadService:
    def __init__(self):
        self.tid = Container.get_tid()
        self.scrape_data_path_builder = Container.get_scrape_data_path_builder()
        self.scrape_logger = Container.get_scrape_logger()
        self.tieba_origin_src_dao = TiebaOriginSrcDao()

    async def save_thread_info(self, thread: Thread_p) -> None:
        try:
            thread_info = ThreadInfo(
                thread.tid,
                thread.title,
                thread.fid,
                thread.fname,
                thread.pid,
                thread.author_id,
                thread.type,
                thread.is_share,
                thread.is_help,
                VoteInfo(
                    thread.vote_info.title,
                    thread.vote_info.is_multi,
                    thread.vote_info.total_vote,
                    thread.vote_info.total_user,
                    list(
                        map(
                            lambda x: VoteOption(x.text, x.vote_num),
                            thread.vote_info.options,
                        )
                    ),
                ),
                thread.share_origin.tid,
                thread.view_num,
                thread.reply_num,
                thread.share_num,
                thread.agree,
                thread.disagree,
                thread.create_time,
            )

            async with aiofiles.open(
                    self.scrape_data_path_builder.get_thread_info_path(self.tid),
                    'w',
                    encoding='utf-8'
            ) as file:
                await file.write(orjson.dumps(thread_info).decode("utf-8"))
            MsgPrinter.print_success(
                "主题帖信息保存成功",
                "SaveThreadInfo",
                [
                    "tid", thread.tid,
                    "title", thread.title
                ]
            )
        except Exception as e:
            MsgPrinter.print_error(str(e), "SaveThreadInfo", ["tid", thread.tid, "title", thread.title])

    async def save_thread_from_share_origin(self, share_origin: ShareThread_pt) -> None:
        try:
            thread_info = ThreadInfo(
                share_origin.tid,
                share_origin.title,
                share_origin.fid,
                share_origin.title,  # title会改成 `原帖被删除`
                0,
                share_origin.author_id,
                0,
                False,
                False,
                VoteInfo(
                    share_origin.vote_info.title,
                    share_origin.vote_info.is_multi,
                    share_origin.vote_info.total_vote,
                    share_origin.vote_info.total_user,
                    list(
                        map(
                            lambda x: VoteOption(x.text, x.vote_num),
                            share_origin.vote_info.options,
                        )
                    ),
                ), 0, 0, 0, 0, 0, 0, 0
            )

            async with aiofiles.open(
                    self.scrape_data_path_builder.get_thread_info_path(self.tid),
                    'w',
                    encoding='utf-8'
            ) as file:
                await file.write(orjson.dumps(thread_info).decode("utf-8"))

            MsgPrinter.print_success(
                "主题帖信息保存成功",
                "SaveThreadInfo-Incomplete(ShareOrigin)",
                [
                    "tid", share_origin.tid,
                    "title", share_origin.title
                ]
            )
        except Exception as e:
            MsgPrinter.print_error(
                str(e),
                "SaveThreadInfo-Incomplete(ShareOrigin)",
                ["tid", share_origin.tid, "title", share_origin.title])

    async def save_forum_info(self, fid: int):
        try:
            forum = await get_forum(fid)
            forum_detail = await get_forum_detail(fid)

            if (forum is None) or (forum_detail is None):
                return

            forum_avatar_dir = (self.scrape_data_path_builder.get_forum_avatar_dir(self.tid))

            small_avatar_filename = self.scrape_data_path_builder.get_forum_small_avatar_filename(forum.fname)
            origin_avatar_filename = self.scrape_data_path_builder.get_forum_origin_avatar_filename(forum.fname)

            try:
                small_avatar_filename = (await download_file(
                    forum_detail.small_avatar,
                    forum_avatar_dir,
                    small_avatar_filename,
                ))[0]
            except Exception as e:
                MsgPrinter.print_error(str(e), "SaveForum-SmallAvatar", ["fid", forum.fid, "fname", forum.fname])
                self.scrape_logger.error(
                    generate_scrape_logger_msg(str(e), "SaveForum-SmallAvatar",
                                               ["fid", forum.fid, "fname", forum.fname])
                )

            try:
                origin_avatar_filename = (await download_file(
                    forum_detail.origin_avatar,
                    forum_avatar_dir,
                    origin_avatar_filename,
                ))[0]
            except Exception as e:
                MsgPrinter.print_error(str(e), "SaveForum-OriginAvatar", ["fid", forum.fid, "fname", forum.fname])
                self.scrape_logger.error(
                    generate_scrape_logger_msg(str(e), "SaveForum-OriginAvatar",
                                               ["fid", forum.fid, "fname", forum.fname])
                )

            forum_info = ForumInfo(
                forum.fid,
                forum.fname,
                forum.category,
                forum.subcategory,
                forum.member_num,
                forum.post_num,
                forum.thread_num,
                forum.slogan,
                small_avatar_filename,
                origin_avatar_filename,
            )

            async with aiofiles.open(
                    self.scrape_data_path_builder.get_forum_info_path(self.tid),
                    'w',
                    encoding='utf-8'
            ) as file:
                await file.write(orjson.dumps(forum_info).decode("utf-8"))

            # 把源连接写入数据库
            self.tieba_origin_src_dao.insert(
                TiebaOriginSrcEntity(
                    small_avatar_filename,
                    ContentFragType.IMAGE,
                    forum_detail.small_avatar,
                )
            )
            self.tieba_origin_src_dao.insert(
                TiebaOriginSrcEntity(
                    origin_avatar_filename,
                    ContentFragType.IMAGE,
                    forum_detail.origin_avatar,
                )
            )

            MsgPrinter.print_success(
                "主题帖的吧信息保存成功",
                "SaveForumInfo",
                [
                    "fid", forum.fid,
                    "fname", forum.fname
                ]
            )
        except Exception as e:
            MsgPrinter.print_error(
                str(e),
                "SaveForumInfo",
                ["fid", fid]
            )
