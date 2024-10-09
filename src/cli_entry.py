import asyncio
import os
import sys

import orjson
import questionary

from modules.scrape_module import scrape
from modules.scrape_update_module import scrape_update
from pojo.enums import ProgramFeatures
from scrape_config import ScrapeConfig
from tieba_auth import TiebaAuth
from utils.msg_printer import PrintColor

TIEBA_AUTH_FILENAME = "tieba_auth.json"
SCRAPE_CONFIG_FILENAME = "scrape_config.json"


def read_tieba_auth() -> None:
    tieba_auth_file_path = os.path.join(os.getcwd(), TIEBA_AUTH_FILENAME)

    try:
        with open(tieba_auth_file_path, "r", encoding="utf-8") as f:
            TiebaAuth.from_dict(orjson.loads(f.read()))
    except Exception:
        BDUSS = questionary.text("未配置BDUSS, 请输入: ").ask()
        TiebaAuth.BDUSS = BDUSS
        with open(tieba_auth_file_path, "w", encoding="utf-8") as f:
            f.write(
                orjson.dumps(
                    TiebaAuth(),
                    option=orjson.OPT_INDENT_2,
                ).decode("utf-8")
            )


def read_scrape_config() -> None:
    scrape_config_file_path = os.path.join(os.getcwd(), SCRAPE_CONFIG_FILENAME)

    try:
        with open(scrape_config_file_path, "r", encoding="utf-8") as f:
            ScrapeConfig.from_dict(orjson.loads(f.read()))
    except FileNotFoundError:
        if questionary.confirm("未找到配置文件, 是否使用默认配置并生成文件?").ask():
            write_scrape_config(scrape_config_file_path)
        else:
            sys.exit()
    except orjson.JSONDecodeError:
        if questionary.confirm("配置文件格式错误导致解析失败, 是否使用默认配置并生成文件?").ask():
            write_scrape_config(scrape_config_file_path)
        else:
            sys.exit()
    except ValueError as err:
        if questionary.confirm(f"配置变量错误: {str(err)}, 是否使用默认配置并生成文件?").ask():
            write_scrape_config(scrape_config_file_path)
        else:
            sys.exit()


def write_scrape_config(path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            orjson.dumps(
                ScrapeConfig(),
                option=orjson.OPT_INDENT_2,
            ).decode("utf-8")
        )


features_choices = [
    questionary.Choice(
        "1. 爬取帖子",
        ProgramFeatures.SCRAPE,
    ),
    questionary.Choice(
        "2. 更新本地的帖子数据",
        ProgramFeatures.SCRAPE_UPDATE,
    ),
    questionary.Choice(
        "3. 导出为可读文件(未实现)",
        ProgramFeatures.EXPORT_TO_READABLE,
    ),
    questionary.Choice(
        "4. 修改爬取配置",
        ProgramFeatures.MODIFY_SCRAPE_CONFIG,
    ),
]


def main():
    while True:
        selected_features = questionary.select("选择功能", choices=features_choices).ask()

        if selected_features == ProgramFeatures.SCRAPE:
            read_tieba_auth()
            read_scrape_config()
            tid = int(questionary.text("请输入要爬取的帖子的tid: ").ask())
            asyncio.run(scrape(tid))
        elif selected_features == ProgramFeatures.SCRAPE_UPDATE:
            read_tieba_auth()
            read_scrape_config()
            path = input("请输入本地帖子数据的路径: ")
            asyncio.run(scrape_update(path))
        elif selected_features == ProgramFeatures.EXPORT_TO_READABLE:
            print(f"{PrintColor.RED}该功能尚未实现{PrintColor.RESET}")
        elif selected_features == ProgramFeatures.MODIFY_SCRAPE_CONFIG:
            print(f"{PrintColor.RED}该功能尚未实现{PrintColor.RESET}")

        input("按下回车键继续...\n")


if __name__ == "__main__":
    main()
