import asyncio
import os
import time
# from ..api.aiotieba_api import get_posts


async def archive_thread(tid: int):
    # tieba_auth
    pass

    # scrape_start_time = time.time()
    # scrape_timestamp = int(scrape_start_time)
    #
    # pre_posts = await get_posts(tid, 1)
    #
    # if pre_posts is None:
    #     print()
    #     # TODO d
    #     return
    #
    # # scrape_path_bulder =
    # save_path_builder = None


class ScrapeThreadDependent:
    tid: int
    # shared_orign:int
    thead_info: dict


    scrape_timestamp: int
    scrape_batch: int

    scrape_config: dict
    tieba_auth: dict

    content_db = None
    scrape_logger = None



    data_path_builder = None
