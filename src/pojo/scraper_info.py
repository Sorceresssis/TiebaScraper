from dataclasses import dataclass, asdict


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
    scraper_version: str
    create_time: int
