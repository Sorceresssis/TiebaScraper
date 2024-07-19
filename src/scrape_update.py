# 在原有数据的基础上跟新新增加的数据
# 新增的数据会在原有数据的基础上进行更新，已经被删除的数据依然会保留，
# 这样就可以最大限度的保留数据，避免数据丢失。

import asyncio

from modules.scrape_update_module import scrape_update


# TODO DROP INDEX index_name

def main():
    path = input("请输入本地要更新帖子的路径: ")
    asyncio.run(scrape_update(path))


if __name__ == "__main__":
    main()
