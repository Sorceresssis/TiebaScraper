from dataclasses import dataclass
from typing import TypedDict, Optional, Dict

from config.scraper_config import SCRAPER_VERSION


class ScrapeRecordDict(TypedDict):
    scrape_time: int
    scrape_config: Dict


@dataclass
class ScrapeInfo:
    """
    This class is used to store information about the scraper.

    Attributes:
        scraper_version (str): The version of the scraper.
        main_thread (int): The main thread ID of the scraper.
    """

    def __init__(self, main_thread: int, create_time: int, scrape_record: ScrapeRecordDict) -> None:
        self.main_thread = main_thread
        self.create_time = create_time
        self.update_time = create_time
        # self.update_times = [] # v1.3.1(删除)
        self.scraper_version = SCRAPER_VERSION

        self.scrape_records = [scrape_record]  # v1.3.1(新增)


class ScrapeInfoDict(TypedDict):
    main_thread: int
    create_time: int
    update_time: int
    update_times: Optional[list[int]]
    scraper_version: str
    scrape_records: Optional[list[ScrapeRecordDict]]
