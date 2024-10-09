from container.container import Container
from pojo.tieba_origin_src_entity import TiebaOriginSrcEntity


class TiebaOriginSrcDao:
    def __init__(self):
        self.db = Container.get_content_db()

    def insert(self, entity: TiebaOriginSrcEntity):
        sql = "INSERT INTO tieba_origin_src (filename, content_frag_type, origin_src) VALUES (?,?,?);"
        self.db.execute(
            sql, (entity.filename, entity.content_frag_type, entity.origin_src,)
        )

    def delete_by_filename(self, filename: str):
        sql = "DELETE FROM tieba_origin_src WHERE filename = ?;"
        self.db.execute(sql, (filename,))
