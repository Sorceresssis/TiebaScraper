from dataclasses import dataclass
from typing import TypedDict, Optional, Dict

from ..config.scraper_config import SCRAPER_VERSION


class ScrapeRecordDict(TypedDict):
    scrape_time: int
    scrape_config: Dict


# TODO JSON 文件中读取的数据建立新的对象,

@dataclass
class ScrapeInfo:
    def __init__(self, main_thread: int, create_time: int, scrape_record: ScrapeRecordDict) -> None:
        self.main_thread = main_thread
        self.create_time = create_time
        self.update_time = create_time
        self.scraper_version = SCRAPER_VERSION

        self.scrape_records = [scrape_record]  # v1.3.1(新增)

    @classmethod
    def from_dict(cls, data):
        return cls(data['name'], data['age'], data['city'])


class ScrapeInfoDict(TypedDict):
    main_thread: int
    create_time: int
    update_time: int
    update_times: Optional[list[int]]
    scraper_version: str
    scrape_records: Optional[list[ScrapeRecordDict]]
