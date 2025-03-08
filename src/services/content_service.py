from urllib.parse import urlparse, parse_qs, quote

import orjson
from aiotieba.api.get_posts._classdef import (
    FragText_p,
    FragEmoji_p,
    FragImage_p,
    FragAt_p,
    FragLink_p,
    FragTiebaPlus_p,
    FragVideo_p,
    FragVoice_p,
)

from ..api.n0099_tbm_v1 import get_custom_emoticon_src
from ..api.tieba_api import TiebaApi
from ..container.container import Container
from ..db.tieba_origin_src_dao import TiebaOriginSrcDao
from ..pojo.content_frag import (
    ContentFragType,
    ContentFrag,
    FragText,
    FragEmoji,
    FragImage,
    FragAt,
    FragLink,
    FragTiebaPlus,
    FragVideo,
    FragVoice,
    FragScrapeError,
)
from ..pojo.tieba_origin_src_entity import TiebaOriginSrcEntity
from ..services.user_service import UserService
from ..utils.fs import download_file
from ..utils.logger import generate_scrape_logger_msg
from ..utils.msg_printer import MsgPrinter


class ContentsAffiliation:
    def __init__(
            self, ppn: int = 1, pid: int = 0, floor: int = 1, cpn: int = 1, cid: int = 0
    ):
        self.ppn = ppn
        self.pid = pid
        self.floor = floor
        self.cpn = cpn
        self.cid = cid


class ContentService:
    def __init__(self):
        self.tid = Container.get_tid()
        self.scrape_data_path_builder = Container.get_scrape_data_path_builder()
        self.scrape_logger = Container.get_scrape_logger()
        self.tieba_origin_src_dao = TiebaOriginSrcDao()
        self.userService = UserService()
        self.post_image_dir = self.scrape_data_path_builder.get_post_image_dir(self.tid)
        self.post_video_dir = self.scrape_data_path_builder.get_post_video_dir(self.tid)
        self.post_voice_dir = self.scrape_data_path_builder.get_post_voice_dir(self.tid)

    # 处理内容
    async def process_contents(
            self, objs: list, affiliation: ContentsAffiliation
    ) -> str:
        contents = list[ContentFrag]()

        for idx, obj in enumerate(objs):
            contents.append(await self.process_frag(obj, idx, affiliation))

        return orjson.dumps(contents).decode("utf-8")

    # 根据类名来获取处理函数
    async def process_frag(
            self, obj, idx: int, affiliation: ContentsAffiliation
    ) -> ContentFrag:
        # 不能让单个frag错误导致整个post失败
        class_name = type(obj).__name__

        if "FragText" in class_name:
            return self.__proc_text_frag(obj)
        elif "FragEmoji" in class_name:
            return self.__proc_emoji_frag(obj, idx, affiliation)
        elif "FragImage" in class_name:
            return await self.__proc_image_frag(obj, idx, affiliation)
        elif "FragAt" in class_name:
            return await self.__proc_at_frag(obj, idx, affiliation)
        elif "FragLink" in class_name:
            return self.__proc_link_frag(obj, idx, affiliation)
        elif "FragTiebaPlus" in class_name:
            return self.__proc_tiebaplus_frag(obj, idx, affiliation)
        elif "FragVideo" in class_name:
            return await self.__proc_video_frag(obj, idx, affiliation)
        elif "FragVoice" in class_name:
            return await self.__proc_voice_frag(obj, idx, affiliation)
        else:
            raise Exception("Unknown FragType")

    # 处理文本
    def __proc_text_frag(self, frag: FragText_p) -> ContentFrag:
        try:
            return FragText(ContentFragType.TEXT, frag.text)
        except Exception as e:
            return FragScrapeError(
                ContentFragType.SCRAPE_ERROR,
                ContentFragType.TEXT,
                "text",
            )

    # 处理表情
    def __proc_emoji_frag(
            self,
            frag: FragEmoji_p,
            idx: int,
            affiliation: ContentsAffiliation
    ) -> ContentFrag:
        try:
            return FragEmoji(ContentFragType.EMOJI, frag.id, frag.desc)
        except Exception as e:
            msg_affiliations = self._generate_content_msg_affiliations(affiliation)
            MsgPrinter.print_error(str(e), "Content-LinkFrag", msg_affiliations)
            self.scrape_logger.error(
                generate_scrape_logger_msg(str(e), "Content-LinkFrag", msg_affiliations)
            )

            return FragScrapeError(
                ContentFragType.SCRAPE_ERROR,
                ContentFragType.EMOJI,
                "emoji",
            )

    # 处理图片
    async def __proc_image_frag(
            self,
            frag: FragImage_p,
            idx: int,
            affiliation: ContentsAffiliation,
    ) -> ContentFrag:
        try:
            # 自定义填字表情包 神来一句 处理
            if frag.origin_src.strip() == "":
                frag.origin_src = (
                        await get_custom_emoticon_src(
                            self.tid,
                            affiliation.ppn,
                            affiliation.pid,
                            affiliation.floor,
                            idx,
                        )
                        or ""
                )

            image_filename = (
                await download_file(
                    frag.origin_src,
                    self.post_image_dir,
                    self.scrape_data_path_builder.get_post_image_filename(
                        affiliation.pid, idx
                    ),
                )
            )[0]

            self.tieba_origin_src_dao.insert(
                TiebaOriginSrcEntity(
                    image_filename, ContentFragType.IMAGE, frag.origin_src
                )
            )
            return FragImage(
                ContentFragType.IMAGE,
                image_filename,
                frag.origin_src,
                frag.origin_size,
                frag.show_width,
                frag.show_height,
                frag.hash,
            )
        except Exception as e:
            msg_affiliations = self._generate_content_msg_affiliations(affiliation)
            MsgPrinter.print_error(str(e), "Content-ImageFrag", msg_affiliations)
            self.scrape_logger.error(
                generate_scrape_logger_msg(str(e), "Content-ImageFrag", msg_affiliations)
            )

            return FragScrapeError(
                ContentFragType.SCRAPE_ERROR,
                ContentFragType.IMAGE,
                "image",
            )

    # 处理AT
    async def __proc_at_frag(
            self,
            frag: FragAt_p,
            idx: int,
            affiliation: ContentsAffiliation
    ) -> ContentFrag:
        try:
            # 有些AT分块的信息不全，user_id会出现0的情况，所以判断一下，防止触发后面的请求错误
            if frag.user_id != 0:
                # 把被AT的用户的信息也存入数据库
                await self.userService.register_user_from_at(frag.user_id, frag.text)
            return FragAt(ContentFragType.AT, frag.text, frag.user_id)
        except Exception as e:
            msg_affiliations = self._generate_content_msg_affiliations(affiliation)
            MsgPrinter.print_error(str(e), "Content-AtFrag", msg_affiliations)
            self.scrape_logger.error(
                generate_scrape_logger_msg(str(e), "Content-AtFrag", msg_affiliations)
            )

            return FragScrapeError(
                ContentFragType.SCRAPE_ERROR,
                ContentFragType.AT,
                "at",
            )

    # 处理链接
    def __proc_link_frag(
            self,
            frag: FragLink_p,
            idx: int,
            affiliation: ContentsAffiliation
    ) -> ContentFrag:
        try:
            # frag.title: a标签的包裹的文本
            # frag.text:对raw_url进行了处理，把`:`, `/` 等字符转义成了 URL编码(百分比编码), eg如下
            # https://tieba.baidu.com/mo/q/checkurl?url=http%3A%2F%2Fwww.baidu.com&urlrefer=02e35c223e4027bc6328d73fafab664f
            # frag.raw_url: 原始连接，可以直接点开, eg如下
            # https://tieba.baidu.com/mo/q/checkurl?url=http://www.baidu.com&urlrefer=02e35c223e4027bc6328d73fafab664f

            raw_url = self.try_extract_tieba_outbound_url(str(frag.raw_url))

            if raw_url == None:
                raise Exception("raw_url is None")

            text = quote(raw_url, safe="")

            return FragLink(ContentFragType.LINK, text, frag.title, raw_url)
        except Exception as e:
            msg_affiliations = self._generate_content_msg_affiliations(affiliation)
            MsgPrinter.print_error(str(e), "Content-LinkFrag", msg_affiliations)
            self.scrape_logger.error(
                generate_scrape_logger_msg(str(e), "Content-LinkFrag", msg_affiliations)
            )
            return FragScrapeError(
                ContentFragType.SCRAPE_ERROR,
                ContentFragType.LINK,
                "link",
            )

    def __proc_tiebaplus_frag(
            self,
            frag: FragTiebaPlus_p,
            idx: int,
            affiliation: ContentsAffiliation,
    ) -> ContentFrag:
        try:
            return FragTiebaPlus(ContentFragType.TIEBAPLUS, frag.text, str(frag.url))
        except Exception as e:
            msg_affiliations = self._generate_content_msg_affiliations(affiliation)
            MsgPrinter.print_error(str(e), "Content-TiebaPlusFrag", msg_affiliations)
            self.scrape_logger.error(
                generate_scrape_logger_msg(str(e), "Content-TiebaPlusFrag", msg_affiliations)
            )
            return FragScrapeError(
                ContentFragType.SCRAPE_ERROR,
                ContentFragType.TIEBAPLUS,
                "tiebaplus",
            )

    # 处理视频
    async def __proc_video_frag(
            self,
            frag: FragVideo_p,
            idx: int,
            affiliation: ContentsAffiliation,
    ) -> ContentFrag:
        try:
            video_filename = (
                await download_file(
                    frag.src,
                    self.post_video_dir,
                    self.scrape_data_path_builder.get_post_video_filename(
                        affiliation.pid, idx
                    ),
                )
            )[0]
            video_cover_filename = (
                await download_file(
                    frag.cover_src,
                    self.post_image_dir,
                    self.scrape_data_path_builder.get_post_image_filename(
                        affiliation.pid, idx
                    ),
                )
            )[0]
            self.tieba_origin_src_dao.insert(
                TiebaOriginSrcEntity(video_filename, ContentFragType.VIDEO, frag.src)
            )
            self.tieba_origin_src_dao.insert(
                TiebaOriginSrcEntity(
                    video_cover_filename,
                    ContentFragType.IMAGE,
                    frag.cover_src,
                )
            )
            return FragVideo(
                ContentFragType.VIDEO,
                video_filename,
                video_cover_filename,
                frag.duration,
                frag.width,
                frag.height,
                frag.view_num,
                frag.src,
                frag.cover_src,
            )
        except Exception as e:
            msg_affiliations = self._generate_content_msg_affiliations(affiliation)
            MsgPrinter.print_error(str(e), "Content-VideoFrag", msg_affiliations)
            self.scrape_logger.error(
                generate_scrape_logger_msg(
                    str(e), "Content-VideoFrag", msg_affiliations
                )
            )

            return FragScrapeError(
                ContentFragType.SCRAPE_ERROR,
                ContentFragType.VIDEO,
                "video",
            )

    # 处理语音
    async def __proc_voice_frag(
            self,
            frag: FragVoice_p,
            idx: int,
            affiliation: ContentsAffiliation,
    ) -> ContentFrag:
        try:
            voice_url = TiebaApi.get_voice_url(frag.md5)
            voice_filename = (
                await download_file(
                    voice_url,
                    self.post_voice_dir,
                    self.scrape_data_path_builder.get_post_voice_filename(affiliation.pid, idx, frag.md5),
                    "amr",
                )
            )[0]
            self.tieba_origin_src_dao.insert(
                TiebaOriginSrcEntity(voice_filename, ContentFragType.VOICE, voice_url)
            )
            return FragVoice(
                ContentFragType.VOICE,
                voice_filename,
                frag.md5,
                frag.duration,
                voice_url,
            )
        except Exception as e:
            msg_affiliations = self._generate_content_msg_affiliations(affiliation)
            MsgPrinter.print_error(str(e), "Content-VoiceFrag", msg_affiliations)

            self.scrape_logger.error(
                generate_scrape_logger_msg(str(e), "Content-VideoFrag", msg_affiliations)
            )

            return FragScrapeError(
                ContentFragType.SCRAPE_ERROR,
                ContentFragType.VOICE,
                "voice",
            )

    @staticmethod
    def try_extract_tieba_outbound_url(raw_url: str) -> str | None:
        url = urlparse(raw_url)
        if url.hostname == "tieba.baidu.com" and url.path == "/mo/q/checkurl":
            query_params = parse_qs(url.query)
            return query_params.get("url", [None])[0]

        return raw_url

    @staticmethod
    def _generate_content_msg_affiliations(affiliation: ContentsAffiliation):
        if affiliation.cid == 0:
            return [
                "floor", affiliation.floor,
                "pid", affiliation.pid,
                "pn", affiliation.ppn,
            ]
        else:
            return [
                "floor", affiliation.floor,
                "pid", affiliation.cid,
                "pn", affiliation.cpn,
                "ppid", affiliation.pid,
                "ppn", affiliation.ppn,
            ]
