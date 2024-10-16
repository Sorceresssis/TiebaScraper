from container.container import Container


class ScrapeBatchDao:
    def __init__(self):
        self.db = Container.get_content_db()

    def insert(self, scraper_version: str, scrape_config: str, scrape_time: int) -> int:
        sql = "INSERT INTO scrape_batch (scraper_version, scrape_config, scrape_time) VALUES (?, ?, ?)"
        cursor = self.db.execute(sql, (scraper_version, scrape_config, scrape_time,))
        return cursor.lastrowid
