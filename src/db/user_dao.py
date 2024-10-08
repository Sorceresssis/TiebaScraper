from asyncio import Lock

from container.container import Container
from pojo.user_entity import UserEntity
from utils.logger import generate_scrape_logger_msg
from utils.msg_printer import MsgPrinter

lock = Lock()


class UserDao:
    def __init__(self):
        self.scrape_logger = Container.get_scrape_logger()
        self.db = Container.get_content_db()

    def check_exists_by_id(self, user_id: int) -> bool:
        sql = "SELECT 1 FROM user WHERE id = ?"
        cursor = self.db.cursor()
        # 创建只包含一个元素的元组需要在后面加上逗号
        cursor.execute(sql, (user_id,))
        return cursor.fetchone() is not None

    def query(self):
        cursor = self.db.cursor()
        cursor.execute(
            """
            SELECT  id, portrait, username, nickname, tieba_uid, avatar,
                    glevel, gender, ip ,is_vip, is_god, age, sign,
                    post_num, agree_num, fan_num, follow_num, forum_num,
                    level, is_bawu, status
            FROM user;"""
        )
        return cursor

    def query_a(self, pid: int):
        cursor = self.db.cursor()
        cursor.execute(
            """
            SELECT u.id, u.portrait, u.username, u.nickname, u.tieba_uid, u.avatar,
                u.glevel, u.gender, u.ip , u.is_vip, u.is_god, u.age, u.sign,
                u.post_num, u.agree_num, u.fan_num, u.follow_num, u.forum_num,
                u.level, u.is_bawu, u.status
            FROM user u JOIN post p ON u.id = p.user_id
            WHERE p.id > ?;
            """,
            (pid,),
        )
        return cursor

    @staticmethod
    def user_entity_factory_from_tuple(tuple_row: tuple | None) -> UserEntity | None:
        if tuple_row is None:
            return None
        return UserEntity(*tuple_row)

    async def insert(self, entity: UserEntity):
        async with lock:
            sql = """
            INSERT INTO user(id, portrait, username, nickname, tieba_uid, avatar, glevel, gender, ip ,is_vip, is_god, age, sign, post_num, agree_num, fan_num, follow_num, forum_num, level, is_bawu, status)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

            try:
                if self.check_exists_by_id(entity.id):
                    return

                self.db.execute(
                    sql,
                    (
                        entity.id,
                        entity.portrait,
                        entity.username,
                        entity.nickname,
                        entity.tieba_uid,
                        entity.avatar,
                        entity.glevel,
                        entity.gender,
                        entity.ip,
                        entity.is_vip,
                        entity.is_god,
                        entity.age,
                        entity.sign,
                        entity.post_num,
                        entity.agree_num,
                        entity.fan_num,
                        entity.follow_num,
                        entity.forum_num,
                        entity.level,
                        entity.is_bawu,
                        entity.status,
                    ),
                )
            except Exception as e:
                MsgPrinter.print_error(str(e), "UserDao.insert", ["entity", entity])
                self.scrape_logger.error(
                    generate_scrape_logger_msg(
                        str(e),
                        "UserDao.insert",
                        ["id", entity.id, "portrait", entity.portrait],
                    )
                )

    def update(self, entity: UserEntity):
        sql = """
        UPDATE user
        SET
        	portrait=?, username=?, nickname=?, tieba_uid=?,
        	avatar=?, glevel=?, gender=?, ip=?, is_vip=?, is_god=?,
        	age=?,sign=?, post_num=?, agree_num=?, fan_num=?,
        	follow_num=?, forum_num=?, level=?, is_bawu=?, status=?
        WHERE id = ?
        """

        self.db.execute(
            sql,
            (
                entity.portrait,
                entity.username,
                entity.nickname,
                entity.tieba_uid,
                entity.avatar,
                entity.glevel,
                entity.gender,
                entity.ip,
                entity.is_vip,
                entity.is_god,
                entity.age,
                entity.sign,
                entity.post_num,
                entity.agree_num,
                entity.fan_num,
                entity.follow_num,
                entity.forum_num,
                entity.level,
                entity.is_bawu,
                entity.status,
                entity.id,
            ),
        )
