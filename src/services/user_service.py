import asyncio

from aiotieba.api.get_comments import UserInfo_c
from aiotieba.api.get_posts import UserInfo_p

from api.aiotieba_client import get_user_info
from api.tieba_api import TiebaApi
from container.container import Container
from db.tieba_origin_src_dao import TiebaOriginSrcDao
from db.user_dao import UserDao
from pojo.content_frag import ContentFragType
from pojo.producer_consumer_contact import ProducerConsumerContact
from pojo.tieba_origin_src_entity import TiebaOriginSrcEntity
from pojo.user_entity import UserEntity
from pojo.user_status import UserStatus
from scrape_config import ScrapeConfig
from utils.fs import download_file
from utils.logger import generate_scrape_logger_msg
from utils.msg_printer import MsgPrinter


class UserService:
    def __init__(self):
        self.tid = Container.get_tid()
        self.scrape_data_path_builder = Container.get_scrape_data_path_builder()
        self.scrape_logger = Container.get_scrape_logger()
        self.user_dao = UserDao()
        self.tieba_origin_src_dao = TiebaOriginSrcDao()
        self.user_avatar_dir = self.scrape_data_path_builder.get_user_avatar_dir(self.tid)
        self.user_cursor = None

    async def register_user_from_post_user(self, user_info: UserInfo_p):
        if not user_info.user_id:
            return
        await self.user_dao.insert(
            UserEntity(
                user_info.user_id,
                user_info.portrait,
                user_info.user_name or None,
                user_info.nick_name_new or "",
                None,  # tieba_uid
                None,  # avatar
                user_info.glevel,
                user_info.gender,
                user_info.ip,
                user_info.is_vip,
                user_info.is_god,
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

    async def register_user_from_comment_user(self, user_info: UserInfo_c):
        if not user_info.user_id:
            return
        await self.user_dao.insert(
            UserEntity(
                user_info.user_id,
                user_info.portrait,
                user_info.user_name or None,
                user_info.nick_name_new or "",
                None,  # tieba_uid
                None,  # avatar
                0,  # glevel
                user_info.gender,
                "",
                user_info.is_vip,
                user_info.is_god,
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

    async def register_user_from_at(self, user_id: int, nickname: str):
        if not user_id:
            return
        # AT 分块只有 user_id 和 nickname。
        # 最终 nickname 以 get_user_info 获取的为准。
        await self.user_dao.insert(UserEntity(user_id, None, None, nickname))

    async def register_user_from_id(self, user_id):
        if not user_id:
            return
        await self.user_dao.insert(UserEntity(user_id))

    async def complete_user_info(self):
        self.user_cursor = self.user_dao.query()
        queue_maxsize = 10
        producers_num = 15
        consumers_num = 10
        consumer_await_timeout = 8
        contact = ProducerConsumerContact(queue_maxsize, producers_num, consumers_num, consumer_await_timeout)

        await asyncio.gather(
            *[self.fetch_user_info(contact) for _ in range(producers_num)],
            *[self.save_user_info(contact) for _ in range(consumers_num)]
        )
        self.user_cursor.close()

    async def fetch_user_info(self, contact: ProducerConsumerContact) -> None:
        while True:
            user_tuple = self.fetchone_user_entity_from_cursor()
            if user_tuple is None:
                break

            user_entity = self.user_dao.user_entity_factory_from_tuple(user_tuple)
            user_info = await get_user_info(user_entity.id, user_entity.portrait)

            if user_info is None:
                user_entity.status = UserStatus.DEACTIVATED
                self.scrape_logger.error(
                    generate_scrape_logger_msg(
                        "", "FetchUserInfo", ["id", user_entity.id, "portrait", user_entity.portrait]
                    )
                )
                await contact.tasks_queue.put(user_entity)
                continue

            # user与其他domain相关联的字段在其他domain保存时就已经保存到了数据库里
            user_entity.portrait = user_info.portrait
            user_entity.username = user_entity.username if user_info.user_name == "-" else user_info.user_name
            user_entity.username = None if user_entity.username == "" else user_entity.username
            user_entity.nickname = user_info.nick_name_new or user_info.nick_name_old or ""
            user_entity.tieba_uid = user_info.tieba_uid or None

            user_entity.glevel = user_info.glevel
            user_entity.gender = user_info.gender
            user_entity.age = user_info.age
            user_entity.post_num = user_info.post_num
            user_entity.agree_num = user_info.agree_num
            user_entity.fan_num = user_info.fan_num
            user_entity.follow_num = user_info.follow_num
            user_entity.forum_num = user_info.forum_num
            user_entity.sign = user_info.sign
            user_entity.ip = user_info.ip

            user_entity.is_vip = user_info.is_vip
            user_entity.is_god = user_info.is_god

            await contact.tasks_queue.put(user_entity)

        # 让最后一个完成的生产者向生产者们发送停止信号，一定要是最后一个！
        # 如果不是最后一个，当其他生产者在等待网络请求时，先完成的生产者会先把停止信号发送给消费者，导致消费者提前退出。
        # 消费者没有消费完还在等待生产的商品就直接退出了.
        contact.running_producers -= 1
        if contact.running_producers == 0:
            for _ in range(contact.consumers_num):
                await contact.tasks_queue.put(None)

    async def save_user_info(self, contact: ProducerConsumerContact):
        while True:
            try:
                user_entity: UserEntity = await asyncio.wait_for(
                    contact.tasks_queue.get(), contact.consumer_await_timeout
                )

                if user_entity is None:
                    return

                if ScrapeConfig.DOWNLOAD_USER_AVATAR_MODE != 0:
                    user_entity.avatar = await self._save_user_avatar(user_entity.id, user_entity.portrait)
                try:
                    self.user_dao.update(user_entity)
                    MsgPrinter.print_success(
                        "",
                        "SaveUserInfo",
                        [
                            "user_id",
                            user_entity.id,
                            "portrait",
                            user_entity.portrait,
                            "user_name",
                            user_entity.username,
                        ],
                    )
                except Exception as e:
                    MsgPrinter.print_error(
                        str(e),
                        "SaveUserInfo",
                        [
                            "user_id",
                            user_entity.id,
                            "portrait",
                            user_entity.portrait,
                            "user_name",
                            user_entity.username,
                        ],
                    )
            except asyncio.TimeoutError:
                if contact.running_producers == 0:
                    return

    async def _save_user_avatar(self, user_id: int, portrait: str) -> None | str:
        if portrait is None:
            return None

        user_avatar_url = TiebaApi.get_user_avatar_url(portrait)

        try:
            avatar_filename = (
                await download_file(
                    user_avatar_url,
                    self.user_avatar_dir,
                    self.scrape_data_path_builder.get_user_avatar_filename(portrait),
                )
            )[0]

            self.tieba_origin_src_dao.insert(
                TiebaOriginSrcEntity(avatar_filename, ContentFragType.IMAGE, user_avatar_url)
            )
            return avatar_filename
        except Exception as e:
            MsgPrinter.print_error(str(e), "SaveUserInfo-Avatar", ["uid", user_id, "portrait", portrait])
            self.scrape_logger.error(
                generate_scrape_logger_msg(
                    str(e), "SaveUserInfo-Avatar", ["uid", user_id, "portrait", portrait]
                )
            )
            return None

    def fetchone_user_entity_from_cursor(self) -> tuple | None:
        return self.user_cursor.fetchone()
