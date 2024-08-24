# 更新本地的帖子数据
# 此过程将帖子新增的数据融入本地数据中。
# 对于已被删除的帖子，会保留本地数据，以避免数据丢失。
# 新发现的帖子将被添加至本地数据，以实现数据的持续扩充和更新。
# 目标是最大程度地保留数据。
# 没有开发完成 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import asyncio

from modules.scrape_update_module import scrape_update
from initial_checks import initial_checks


def main():
    initial_checks()
    path = input("请输入本地帖子数据的路径: ")
    asyncio.run(scrape_update(path))


if __name__ == "__main__":
    main()
