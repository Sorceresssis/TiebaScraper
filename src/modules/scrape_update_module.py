import os
import time

import orjson

from api.aiotieba_client import get_posts
from config.path_config import ScrapeDataPathBuilder
from container.container import Container
from pojo.scraper_info import ScraperInfoDict
from utils.msg_printer import MsgPrinter


async def scrape_update(path: str):
    if not os.path.isdir(path):
        MsgPrinter.print_error("输入的路径不存在", "ScrapeUpdate", )
        return

    scrape_data_path_builder = ScrapeDataPathBuilder.get_instance_scrape_update(path)
    Container.set_scrape_data_path_builder(scrape_data_path_builder)

    scrape_info_path = scrape_data_path_builder.get_scrape_info_path()
    if not os.path.isfile(scrape_info_path):
        MsgPrinter.print_error("未找到ScrapeInfo文件", "ScrapeUpdate", )
        return

    data: ScraperInfoDict
    with open(scrape_info_path, 'r') as file:
        data = orjson.loads(file.read())

    update_time: float = time.time()
    updating_tid = data["main_thread"]
    # 先加载一次, 触发网络连接问题
    await get_posts(updating_tid)

    while updating_tid != 0:
        pre_post = await get_posts(updating_tid)

        if pre_post is None:
            MsgPrinter.print_error("")

        # TODO step 1 遍历 pn， 找到 最后一楼的pid。如果小于直接跳过。savePost. 交给comment.
        # TODO step 2 找到最新的 每楼的最新pid。 小于等于直接跳过

        # TODO step 3 多版本数据库适配  DROP INDEX xxx

        # 读取 thread_info
        thread_info_dict = {}
        with open(scrape_data_path_builder.get_thread_info_path(updating_tid), 'r') as file:
            thread_info_dict = orjson.loads(file.read())

        thread_info_dict["share_origin"]

    data["update_record"].append(int(update_time))
    with open(scrape_info_path, 'w') as file:
        file.write(orjson.dumps(data).decode("utf-8"))

    MsgPrinter.print_info("ScrapeUpdate完成", "ScrapeUpdate", )
    MsgPrinter.print_step_mark("")
