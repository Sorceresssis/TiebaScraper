import asyncio

import questionary

from modules.scrape_module import scrape
from pojo.enums import ProgramFeatures
from utils.msg_printer import PrintColor
import os

import orjson


features_choices = [
    questionary.Choice(
        "1. 爬取帖子",
        ProgramFeatures.SCRAPE,
    ),
    questionary.Choice(
        "2. 更新本地的帖子数据(未实现)",
        ProgramFeatures.SCRAPE_UPDATE,
    ),
    questionary.Choice(
        "3. 导出为可读文件(未实现)",
        ProgramFeatures.EXPORT_TO_READABLE,
    ),
]


def main():
    while True:
        selected_features = questionary.select("选择功能", choices=features_choices).ask()

        if selected_features == ProgramFeatures.SCRAPE:
            tid = int(questionary.text("请输入要爬取的帖子的tid: ").ask())
            asyncio.run(scrape(tid))
        elif selected_features == ProgramFeatures.SCRAPE_UPDATE:
            # questionary.path
            print(f"{PrintColor.RED}该功能尚未实现{PrintColor.RESET}")
        elif selected_features == ProgramFeatures.EXPORT_TO_READABLE:
            print(f"{PrintColor.RED}该功能尚未实现{PrintColor.RESET}")

        # 按下任意键继续
        input("按下回车键继续...\n")


if __name__ == "__main__":
    main()


TIEBA_AUTH_FILENAME = "tieba_auth.json"
SCRAPE_CONFIG_FILENAME = "scrape_config.json"


def read_tieba_auth():
    tieba_auth_file_path = os.path.join(os.getcwd(), TIEBA_AUTH_FILENAME)

    try:
        with open(tieba_auth_file_path, "r", encoding="utf-8") as f:
            user_tieba_auth = TiebaAuth.from_dict(orjson.loads(f.read()))
    except Exception:
        BDUSS = input("BDUSS 未找到，请输入 BDUSS: ")
        user_tieba_auth = get_tieba_auth()
        with open(tieba_auth_file_path, "w", encoding="utf-8") as f:
            f.write(
                orjson.dumps(
                    user_tieba_auth,
                    option=orjson.OPT_INDENT_2,
                ).decode("utf-8")
            )

    return user_tieba_auth


def read_scrape_config() -> ScrapeConfig:
    scrape_config_file_path = os.path.join(os.getcwd(), SCRAPE_CONFIG_FILENAME)

    user_scrape_config: ScrapeConfig
    try:
        with open(scrape_config_file_path, "r", encoding="utf-8") as f:
            user_scrape_config = ScrapeConfig.from_dict(orjson.loads(f.read()))
    except:
        user_scrape_config = get_scrape_config()

        with open(scrape_config_file_path, "w", encoding="utf-8") as f:
            f.write(
                orjson.dumps(
                    user_scrape_config,
                    option=orjson.OPT_INDENT_2,
                ).decode("utf-8")
            )
    return user_scrape_config
