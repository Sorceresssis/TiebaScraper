from container.container import Container
from pojo.post_entity import PostEntity


class PostDao:
    def __init__(self):
        self.db = Container.get_content_db()

    def post_entity_factory_from_tuple(self, tuple_row: tuple | None) -> PostEntity | None:
        if tuple_row is None:
            return None
        return PostEntity(*tuple_row)

    def query_latest_post(self) -> PostEntity | None:
        sql = "SELECT id, contents, floor, user_id, agree, disagree, create_time, is_thread_author, sign, reply_num, parent_id, reply_to_id FROM post WHERE parent_id = 0 ORDER BY id DESC LIMIT 1;"
        cursor = self.db.execute(sql)
        return self.post_entity_factory_from_tuple(cursor.fetchone())

    def query_latest_sub_post_by_pid(self, pid: int) -> PostEntity | None:
        sql = "SELECT id, contents, floor, user_id, agree, disagree, create_time, is_thread_author, sign, reply_num, parent_id, reply_to_id FROM post WHERE parent_id = ? ORDER BY id DESC LIMIT 1;"
        cursor = self.db.execute(sql, (pid,))
        return self.post_entity_factory_from_tuple(cursor.fetchone())

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

    def update_post_traffic_by_id(self, pid: int, agree: int, disagree: int, reply_num: int):
        sql = "UPDATE post SET agree = ?, disagree = ?, reply_num = ? WHERE id = ?;"
        self.db.execute(sql, (agree, disagree, reply_num, pid))
