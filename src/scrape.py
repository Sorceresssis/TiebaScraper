import os
import time
import orjson
from net.aiotieba_client import get_posts
from utils.logger import ScrapeLogger
from config.scraper_config import SCRAPER_VERSION
from config.path_config import ScrapedPathConstructor
from container import Container
from db.content_db import ContentDB
from pojo.scraper_info import ScraperInfo
from services.thread_service import ThreadService


async def scrape(tid: int):
    task_start_time = time.time()

    posts = await get_posts(tid)
    if posts.thread.tid == 0:
        print("Error: 帖子不存在, 请检查tid")
        return

    scraped_path_constructor = ScrapedPathConstructor(
        posts.forum.fname, posts.thread.tid, posts.thread.title
    )

    # 路径构造器注入到全局容器
    Container.set_scraped_path_constructor(scraped_path_constructor)
    scrape_logger = ScrapeLogger(scraped_path_constructor.get_scrape_log_path())
    Container.set_scrape_logger(scrape_logger)

    scraper_info = ScraperInfo(tid, SCRAPER_VERSION, int(time.time()))
    with open(
        scraped_path_constructor.get_scraper_info_path(), "w", encoding="utf-8"
    ) as file:
        file.write(orjson.dumps(scraper_info).decode("utf-8"))

    scrape_thread_id = tid
    while scrape_thread_id != 0:
        # 创建目录
        os.makedirs(
            scraped_path_constructor.get_thread_dir(scrape_thread_id),
            exist_ok=True,
        )
        # 把正在爬取的tid注入到全局容器
        Container.set_tid(scrape_thread_id)
        # 把数据库注入到全局容器
        Container.set_content_db(
            ContentDB(scraped_path_constructor.get_content_db_path(scrape_thread_id))
        )

        # 依赖注入完成，开始爬取
        thread_servie = ThreadService()
        await thread_servie.scrape()

        scrape_thread_id = thread_servie.get_share_origin()
        if scrape_thread_id != 0:
            msg = f"这是一个分享帖, 下面将爬取它的原帖: {scrape_thread_id}"
            print(msg)
            scrape_logger.info(msg)

    task_end_time = time.time()
    task_duration = task_end_time - task_start_time

    scrape_logger.info("爬取任务完成")
    print(
        f"爬取完成, 耗时 {task_duration // 60} 分 { round(task_duration % 60, 2)} 秒。 \n帖子数据保存在: {scraped_path_constructor.get_scraped_data_dir()}"
    )
