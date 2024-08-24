import asyncio
import os
from dataclasses import dataclass
from typing import Dict, Any

import orjson
import questionary

import scrape_config
import tieba_auth
from modules.scrape_module import scrape
from pojo.enums import ProgramFeatures
from utils.msg_printer import PrintColor

from initial_checks import initial_checks


@dataclass
class TiebaAuth:
    BDUSS: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "TiebaAuth":
        return TiebaAuth(**data)


@dataclass
class ScrapeConfig:
    download_user_avatar_mode: int
    scrape_share_origin: bool
    update_forum_avatar_on_update: bool

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ScrapeConfig":
        return ScrapeConfig(**data)


TIEBA_AUTH_FILENAME = "tieba_auth.json"
SCRAPE_CONFIG_FILENAME = "scrape_config.json"


def read_tieba_auth():
    tieba_auth_file_path = os.path.join(os.getcwd(), TIEBA_AUTH_FILENAME)

    try:
        with open(tieba_auth_file_path, "r", encoding="utf-8") as f:
            user_tieba_author = TiebaAuth(orjson.loads(f.read()))
            tieba_auth.BDUSS = user_tieba_author.BDUSS
    except Exception:
        BDUSS = input("BDUSS 未找到，请输入 BDUSS: ")
        tieba_auth.BDUSS = BDUSS
        with open(tieba_auth_file_path, "w", encoding="utf-8") as f:
            f.write(
                orjson.dumps(
                    TiebaAuth(BDUSS=BDUSS),
                    option=orjson.OPT_INDENT_2,
                ).decode("utf-8")
            )


def read_scrape_config():
    scrape_config_file_path = os.path.join(os.getcwd(), SCRAPE_CONFIG_FILENAME)
    try:
        with open(scrape_config_file_path, "r", encoding="utf-8") as f:
            user_scrape_config = ScrapeConfig.from_dict(orjson.loads(f.read()))

            scrape_config.DOWNLOAD_USER_AVATAR_MODE = user_scrape_config.download_user_avatar_mode
            scrape_config.SCRAPE_SHARE_ORIGIN = user_scrape_config.scrape_share_origin
            scrape_config.UPDATE_FORUM_AVATAR_ON_UPDATE = user_scrape_config.update_forum_avatar_on_update

    except:
        with open(scrape_config_file_path, "w", encoding="utf-8") as f:
            f.write(
                orjson.dumps(
                    ScrapeConfig(
                        scrape_config.DOWNLOAD_USER_AVATAR_MODE,
                        scrape_config.SCRAPE_SHARE_ORIGIN,
                        scrape_config.UPDATE_FORUM_AVATAR_ON_UPDATE,
                    ),
                    option=orjson.OPT_INDENT_2,
                ).decode("utf-8")
            )


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
            read_tieba_auth()
            read_scrape_config()
            initial_checks()
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
