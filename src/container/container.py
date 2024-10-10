from config.path_config import ScrapeDataPathBuilder
from db.content_db import ContentDB
from utils.logger import ScrapeLogger


class Container:
    scrape_data_path_builder: ScrapeDataPathBuilder | None = None
    tid: int = 0
    scrape_timestamp: int = 0
    scrape_logger: ScrapeLogger | None = None  # 依赖scraped_path_constructor
    content_db: ContentDB | None = None

    @classmethod
    def get_scrape_data_path_builder(cls) -> ScrapeDataPathBuilder:
        if cls.scrape_data_path_builder is None:
            raise Exception("ScrapeDataPathBuilder is not set")
        return cls.scrape_data_path_builder

    @classmethod
    def set_scrape_data_path_builder(cls, scrape_data_path_builder: ScrapeDataPathBuilder) -> None:
        cls.scrape_data_path_builder = scrape_data_path_builder

    @classmethod
    def get_tid(cls) -> int:
        if cls.tid == 0:
            raise Exception("tid is not set")

        return cls.tid

    @classmethod
    def set_tid(cls, tid: int) -> None:
        cls.tid = tid

        # NOTE 依赖tid的属性，再设置tid时全部重置。
        cls.scrape_logger = None
        cls.content_db = None

    @classmethod
    def set_scrape_timestamp(cls, timestamp: int) -> None:
        cls.scrape_timestamp = timestamp

    @classmethod
    def get_scrape_timestamp(cls) -> int:
        if cls.scrape_timestamp == 0:
            raise Exception("scrape_timestamp is not set")
        return cls.scrape_timestamp

    @classmethod
    def get_scrape_logger(cls):
        if cls.scrape_logger is None:
            cls.scrape_logger = ScrapeLogger(
                cls.get_scrape_data_path_builder().get_scrape_log_path(cls.tid, cls.scrape_timestamp))

        return cls.scrape_logger

    @classmethod
    def get_content_db(cls) -> ContentDB:
        if cls.content_db is None:
            cls.content_db = ContentDB(
                cls.get_scrape_data_path_builder().get_content_db_path(cls.tid),
                cls.tid,
            )

        return cls.content_db
