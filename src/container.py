from config.path_config import ScrapedPathConstructor
from utils.logger import ScrapeLogger
from db.content_db import ContentDB


class Container:
    tid: int = 0
    # scraped_path_constructor 部分功能依赖于tid
    scraped_path_constructor: ScrapedPathConstructor | None = None
    scrape_logger: ScrapeLogger | None  # 依赖于scraped_path_constructor
    content_db: ContentDB | None

    @classmethod
    def get_tid(cls) -> int:
        return cls.tid

    @classmethod
    def set_tid(cls, tid: int) -> None:
        cls.tid = tid

    @classmethod
    def set_scraped_path_constructor(
        cls, scraped_path_constructor: ScrapedPathConstructor
    ) -> None:
        cls.scraped_path_constructor = scraped_path_constructor

    @classmethod
    def get_scraped_path_constructor(cls) -> ScrapedPathConstructor:
        if cls.scraped_path_constructor is None:
            raise Exception("ScrapedPathConstructor is not set")
        return cls.scraped_path_constructor

    @classmethod
    def get_scrape_logger(cls):
        if cls.scrape_logger is None:
            raise Exception("ScrapeLogger is not set")
        return cls.scrape_logger

    @classmethod
    def set_scrape_logger(cls, scrape_logger: ScrapeLogger):
        cls.scrape_logger = scrape_logger

    @classmethod
    def set_content_db(cls, content_db: ContentDB):
        cls.content_db = content_db

    @classmethod
    def get_content_db(cls) -> ContentDB:
        if cls.content_db is None:
            raise Exception("ContentDB is not set")
        return cls.content_db
