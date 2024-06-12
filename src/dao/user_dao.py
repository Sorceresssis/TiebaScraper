from container import Container
from entity.user_entity import UserEntity


class UserDao:
    def __init__(self):
        self.db = Container.get_content_db()

    def check_exists_by_id(self, user_id: int) -> bool:
        sql = "SELECT 1 FROM user WHERE id = ?"
        cursor = self.db.cursor()
        cursor.execute(sql, (user_id,))
        return cursor.fetchone() is not None

    def insert(self, entity: UserEntity):
        sql = """
        INSERT INTO user(id, portrait, username, nickname, avatar, glevel, gender, ip ,is_vip, is_god, tieba_uid, age, sign, post_num, agree_num, fan_num, follow_num, forum_num, level, is_bawu, status)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            self.db.execute(
                sql,
                (
                    entity.id,
                    entity.portrait,
                    entity.username,
                    entity.nickname,
                    entity.avatar,
                    entity.glevel,
                    entity.gender,
                    entity.ip,
                    entity.is_vip,
                    entity.is_god,
                    entity.tieba_uid,
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
            print("出错entity：", entity)
            print(e)
