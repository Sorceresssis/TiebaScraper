import orjson
from urllib.parse import urlparse, parse_qs, quote
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
from config.constant_config import get_voice_url
from utils.fs import download_file
from container import Container
from pojo.content_frag import (
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
from entity.tieba_origin_src_entity import TiebaOriginSrcEntity
from dao.tieba_origin_src_dao import TiebaOriginSrcDao
from services.user_service import UserService
from net.n0099_tbm_v1 import get_custom_emoticon_src


class ContentService:
    def __init__(self):
        self.pid = 0
        self.floor = 0
        self.tid = Container.get_tid()
        self.scraped_path_constructor = Container.get_scraped_path_constructor()
        self.tieba_origin_src_dao = TiebaOriginSrcDao()
        self.post_image_dir = self.scraped_path_constructor.get_post_image_dir(self.tid)
        self.post_video_dir = self.scraped_path_constructor.get_post_video_dir(self.tid)
        self.post_voice_dir = self.scraped_path_constructor.get_post_voice_dir(self.tid)
        self.userService = UserService()

    # 处理内容
    async def process_contents(self, pid: int, floor, objs: list) -> str:
        self.pid = pid
        self.floor = floor
        contents = list[ContentFrag]()

        for idx, obj in enumerate(objs):
            contents.append(await self.get_proced_frag(obj, idx))

        return orjson.dumps(contents).decode("utf-8")

    # 根据类名来获取处理函数
    async def get_proced_frag(self, obj, idx: int) -> ContentFrag:
        # 不能让单个frag错误导致整个post失败
        class_name = type(obj).__name__

        if "FragText" in class_name:
            return self.__proc_text_frag(obj)
        elif "FragEmoji" in class_name:
            return self.__proc_emoji_frag(obj)
        elif "FragImage" in class_name:
            return await self.__proc_image_frag(obj, idx)
        elif "FragAt" in class_name:
            return await self.__proc_at_frag(obj)
        elif "FragLink" in class_name:
            return self.__proc_link_frag(obj)
        elif "FragTiebaPlus" in class_name:
            return self.__proc_tiebaplus_frag(obj)
        elif "FragVideo" in class_name:
            return self.__proc_video_frag(obj)
        elif "FragVoice" in class_name:
            return self.__proc_voice_frag(obj)
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
    def __proc_emoji_frag(self, frag: FragEmoji_p) -> ContentFrag:
        try:
            return FragEmoji(ContentFragType.EMOJI, frag.id, frag.desc)
        except:
            return FragScrapeError(
                ContentFragType.SCRAPE_ERROR,
                ContentFragType.EMOJI,
                "emoji",
            )

    # 处理图片
    async def __proc_image_frag(self, frag: FragImage_p, idx: int) -> ContentFrag:
        try:
            # TODO 自定义填字表情包 神来一句
            if frag.origin_src.strip() == "":
                frag.origin_src = (
                    await get_custom_emoticon_src(
                        self.tid,
                        Container.get_current_posts_pn(),
                        self.pid,
                        self.floor,
                        idx,
                    )
                    or ""
                )

            image_filename = download_file(
                frag.origin_src,
                self.post_image_dir,
                self.scraped_path_constructor.get_post_image_filename(self.pid),
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
        except:
            return FragScrapeError(
                ContentFragType.SCRAPE_ERROR,
                ContentFragType.IMAGE,
                "image",
            )

    # 处理AT
    async def __proc_at_frag(self, frag: FragAt_p) -> ContentFrag:
        try:
            # 把被AT的用户的信息也存入数据库
            await self.userService.save_user_by_id(frag.user_id)
            return FragAt(ContentFragType.AT, frag.text, frag.user_id)
        except:
            return FragScrapeError(
                ContentFragType.SCRAPE_ERROR,
                ContentFragType.AT,
                "at",
            )

    # 处理链接
    def __proc_link_frag(self, frag: FragLink_p) -> ContentFrag:
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
        except:
            return FragScrapeError(
                ContentFragType.SCRAPE_ERROR,
                ContentFragType.LINK,
                "link",
            )

    def try_extract_tieba_outbound_url(self, raw_url: str) -> str | None:
        url = urlparse(raw_url)
        if url.hostname == "tieba.baidu.com" and url.path == "/mo/q/checkurl":
            query_params = parse_qs(url.query)
            return query_params.get("url", [None])[0]

        return raw_url

    def __proc_tiebaplus_frag(self, frag: FragTiebaPlus_p) -> ContentFrag:
        try:
            return FragTiebaPlus(ContentFragType.TIEBAPLUS, frag.text, str(frag.url))
        except:
            return FragScrapeError(
                ContentFragType.SCRAPE_ERROR,
                ContentFragType.TIEBAPLUS,
                "tiebaplus",
            )

    # 处理视频
    def __proc_video_frag(self, frag: FragVideo_p) -> ContentFrag:
        try:
            video_filename = download_file(
                frag.src,
                self.post_video_dir,
                self.scraped_path_constructor.get_post_video_filename(self.pid),
            )[0]
            video_cover_filename = download_file(
                frag.cover_src,
                self.post_image_dir,
                self.scraped_path_constructor.get_post_image_filename(self.pid),
            )[0]
            self.tieba_origin_src_dao.insert(
                TiebaOriginSrcEntity(video_filename, ContentFragType.VIDEO, frag.src)
            )
            self.tieba_origin_src_dao.insert(
                TiebaOriginSrcEntity(
                    video_cover_filename, ContentFragType.IMAGE, frag.cover_src
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
        except:
            return FragScrapeError(
                ContentFragType.SCRAPE_ERROR,
                ContentFragType.VIDEO,
                "video",
            )

    # 处理语音
    def __proc_voice_frag(self, frag: FragVoice_p) -> ContentFrag:
        try:
            voice_url = get_voice_url(frag.md5)
            voice_filename = download_file(
                voice_url,
                self.post_voice_dir,
                self.scraped_path_constructor.get_post_voice_filename(self.pid),
                "amr",
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
        except:
            return FragScrapeError(
                ContentFragType.SCRAPE_ERROR,
                ContentFragType.VOICE,
                "voice",
            )
