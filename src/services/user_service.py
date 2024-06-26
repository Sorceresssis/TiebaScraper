from aiotieba.api.get_posts import UserInfo_p
from aiotieba.api.get_comments import UserInfo_c
from net.aiotieba_client import get_user_info
from config.constant_config import get_user_avatar_url
from utils.fs import download_file
from container import Container
from dao.user_dao import UserDao
from dao.tieba_origin_src_dao import TiebaOriginSrcDao
from entity.user_entity import UserEntity
from entity.tieba_origin_src_entity import TiebaOriginSrcEntity
from pojo.content_frag import ContentFragType
from pojo.user_status import UserStatus


class UserService:
    def __init__(self):
        self.scraped_path_constructor = Container.get_scraped_path_constructor()
        self.user_dao = UserDao()
        self.tieba_origin_src_dao = TiebaOriginSrcDao()
        self.user_avatar_dir = self.scraped_path_constructor.get_user_avatar_dir(
            Container.get_tid()
        )
        self.scrape_logger = Container.get_scrape_logger()

    async def save_user_info_by_uip(self, user_info: UserInfo_p):
        if self.user_dao.check_exists_by_id(user_info.user_id):
            return
        await self.save_user_info(
            UserEntity(
                user_info.user_id,
                user_info.portrait,
                user_info.user_name or None,
                user_info.nick_name_new
                or user_info.nick_name
                or user_info.user_name
                or "",
                "",  # avatar
                user_info.glevel,
                user_info.gender,
                user_info.ip,
                user_info.is_vip,
                user_info.is_god,
                None,  # tieba_uid
                0,  # age
                "",  # sign
                0,  # post_num
                0,  # agree_num
                0,  # fan_num
                0,  # follow_num
                0,  # forum_num
                user_info.level,
                user_info.is_bawu,
                UserStatus.ACTIVE,
            )
        )

    async def save_user_info_by_uic(self, user_info: UserInfo_c):
        # 查询用户是否已经保存
        if self.user_dao.check_exists_by_id(user_info.user_id):
            return

        await self.save_user_info(
            UserEntity(
                user_info.user_id,
                user_info.portrait,
                user_info.user_name or None,
                user_info.nick_name_new
                or user_info.nick_name
                or user_info.user_name
                or "",
                "",  # avatar
                0,  # glevel
                user_info.gender,
                "",
                user_info.is_vip,
                user_info.is_god,
                None,  # tieba_uid
                0,  # age,
                "",  # sign
                0,  # post_num
                0,  # agree_num
                0,  # fan_num
                0,  # follow_num
                0,  # forum_num
                user_info.level,
                user_info.is_bawu,
                UserStatus.ACTIVE,
            )
        )

    async def save_user_info(self, user_entity: UserEntity):
        # 有可能会请求失败, 重试2次，如果依然失败，判定为用户已经注销。
        user_info = None
        retry = 3
        while user_info is None and retry:
            user_info = await get_user_info(user_entity.id)
            retry -= 1

        if user_info:
            user_entity.glevel = user_info.glevel
            user_entity.ip = user_info.ip
            user_entity.tieba_uid = user_info.tieba_uid or None
            user_entity.age = user_info.age
            user_entity.sign = user_info.sign
            user_entity.post_num = user_info.post_num
            user_entity.agree_num = user_info.agree_num
            user_entity.fan_num = user_info.fan_num
            user_entity.follow_num = user_info.follow_num
            user_entity.forum_num = user_info.forum_num
        else:
            # 如果用户已经注销不存在, 就会抛出异常
            print(f"用户: {user_entity.id} 已注销。")
            user_entity.status = UserStatus.DEACTIVATED
            self.scrape_logger.warning(
                f"用户: {user_entity.id} 已注销。portrait={user_entity.portrait}"
            )

        user_avatar_url = get_user_avatar_url(user_entity.portrait)

        try:
            user_entity.avatar = download_file(
                user_avatar_url,
                self.user_avatar_dir,
                self.scraped_path_constructor.get_user_avatar_filename(user_entity.id),
            )[0]

            # 写入tieba_origin_src表
            self.tieba_origin_src_dao.insert(
                TiebaOriginSrcEntity(
                    user_entity.avatar, ContentFragType.IMAGE, user_avatar_url
                )
            )

        except Exception as e:
            print(f"下载用户头像失败, user_id={user_entity.id}, url={user_avatar_url}")
            self.scrape_logger.error(
                f"下载用户头像失败, user_id={user_entity.id}, url={user_avatar_url}, 错误描述:{e}"
            )

        self.user_dao.insert(user_entity)

    async def save_user_by_id(self, user_id: int):
        # 查询用户是否已经保存
        if self.user_dao.check_exists_by_id(user_id):
            return

        user_info = None
        retry = 3
        while user_info is None and retry:
            user_info = await get_user_info(user_id)
            retry -= 1

        if not user_info:
            return

        user_entity = UserEntity(
            user_info.user_id,
            user_info.portrait,
            user_info.user_name,
            user_info.nick_name_new,
            "",
            user_info.glevel,
            user_info.gender,
            user_info.ip,
            user_info.is_vip,
            user_info.is_god,
            user_info.tieba_uid,
            user_info.age,
            user_info.sign,
            user_info.post_num,
            user_info.agree_num,
            user_info.fan_num,
            user_info.follow_num,
            user_info.forum_num,
            0,
            False,
            UserStatus.ACTIVE,
        )

        user_avatar_url = get_user_avatar_url(user_entity.portrait)

        try:
            user_entity.avatar = download_file(
                user_avatar_url,
                self.user_avatar_dir,
                self.scraped_path_constructor.get_user_avatar_filename(user_entity.id),
            )[0]

            # 写入tieba_origin_src表
            self.tieba_origin_src_dao.insert(
                TiebaOriginSrcEntity(
                    user_entity.avatar, ContentFragType.IMAGE, user_avatar_url
                )
            )

        except Exception as e:
            print(f"下载用户头像失败, user_id={user_entity.id}, url={user_avatar_url}")
            self.scrape_logger.error(
                f"下载用户头像失败, user_id={user_entity.id}, url={user_avatar_url}, 错误描述:{e}"
            )

        self.user_dao.insert(user_entity)
