from container.container import Container


class ScrapeBatchDao:
    def __init__(self):
        self.db = Container.get_content_db()

    def insert(self):
        pass
