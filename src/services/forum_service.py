import orjson
from pojo.forum_info import ForumInfo
from net.aiotieba_client import get_forum, get_forum_detail
from utils.fs import download_file
from container import Container
from dao.tieba_origin_src_dao import TiebaOriginSrcDao
from entity.tieba_origin_src_entity import TiebaOriginSrcEntity
from pojo.content_frag import ContentFragType


class ForumService:
    def __init__(self, fid: int) -> None:
        self.fid = fid
        self.tieba_origin_src_dao = TiebaOriginSrcDao()
        self.scraped_path_constructor = Container.get_scraped_path_constructor()
        self.scrape_logger = Container.get_scrape_logger()

    async def save_forum_info(self):
        forum = await get_forum(self.fid)
        forum_detail = await get_forum_detail(self.fid)

        forum_avatar_dir = self.scraped_path_constructor.get_forum_avatar_dir(
            Container.get_tid()
        )

        small_avatar_filename = "f_small_avatar"
        origin_avatar_filename = "f_origin_avatar"

        try:
            small_avatar_filename = download_file(
                forum_detail.small_avatar,
                forum_avatar_dir,
                small_avatar_filename,
            )[0]
        except Exception as e:
            self.scrape_logger.error(
                f"贴吧小头像下载失败, url={forum_detail.small_avatar}  错误描述:{e}"
            )

        try:
            origin_avatar_filename = download_file(
                forum_detail.origin_avatar,
                forum_avatar_dir,
                origin_avatar_filename,
            )[0]
        except Exception as e:
            self.scrape_logger.error(
                f"贴吧头像下载失败, url={forum_detail.origin_avatar}  错误描述:{e}"
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

        with open(
            self.scraped_path_constructor.get_forum_info_path(Container.get_tid()),
            "w",
            encoding="utf-8",
        ) as file:
            file.write(orjson.dumps(forum_info).decode("utf-8"))

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
