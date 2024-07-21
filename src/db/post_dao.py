from container.container import Container
from pojo.post_entity import PostEntity


class PostDao:
    def __init__(self):
        self.db = Container.get_content_db()

    def query_latest_response_time_of_floor(self, floor: int):
        sql = """
        """
        self.db.execute(sql, )

    def insert(self, entity: PostEntity):
        sql = """
        INSERT INTO post(id, contents, floor, user_id, agree, disagree, create_time, is_thread_author, sign, reply_num, parent_id, reply_to_id)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        self.db.execute(
            sql,
            (
                entity.id,
                entity.contents,
                entity.floor,
                entity.user_id,
                entity.agree,
                entity.disagree,
                entity.create_time,
                entity.is_thread_author,
                entity.sign,
                entity.reply_num,
                entity.parent_id,
                entity.reply_to_id,
            ),
        )
