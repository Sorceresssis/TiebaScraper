import asyncio
from scrape import scrape


def main():
    tid = int(input("请输入要爬取的贴子tid: "))
    asyncio.run(scrape(tid))


if __name__ == "__main__":
    main()
