import time
from dataclasses import dataclass
from typing import TypedDict

from config.scraper_config import SCRAPER_VERSION


@dataclass
class ScraperInfo:
    """
    This class is used to store information about the scraper.

    Attributes:
        scraper_version (str): The version of the scraper.
        main_thread (int): The main thread ID of the scraper.
        gmt_create (int): The GMT time when the scraper was created.
    """

    main_thread: int
    create_time: int
    update_record: list[str]
    scraper_version: str

    def __init__(self, main_thread: int) -> None:
        self.main_thread = main_thread
        self.create_time = int(time.time())
        self.update_times = []
        self.scraper_version = SCRAPER_VERSION


class ScraperInfoDict(TypedDict):
    main_thread: int
    create_time: int
    update_times: list[int]
    scraper_version: str
