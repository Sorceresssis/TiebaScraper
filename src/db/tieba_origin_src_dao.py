from pojo.tieba_origin_src_entity import TiebaOriginSrcEntity
from container.container import Container


class TiebaOriginSrcDao:
    def __init__(self):
        self.db = Container.get_content_db()

    def insert(self, entity: TiebaOriginSrcEntity):
        sql = "INSERT INTO tieba_origin_src (filename, content_frag_type, origin_src) VALUES (?,?,?);"
        self.db.execute(
            sql, (entity.filename, entity.content_frag_type, entity.origin_src)
        )
