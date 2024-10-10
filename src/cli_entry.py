import asyncio
import os
import sys

import orjson
import questionary

from modules.scrape_module import scrape
from modules.scrape_update_module import scrape_update
from pojo.enums import ProgramFeatures
from scrape_config import DownloadUserAvatarModeEnum, ScrapeConfig, ScrapeConfigKeysEnum
from tieba_auth import TiebaAuth
from utils.msg_printer import PrintColor

TIEBA_AUTH_FILENAME = "tieba_auth.json"


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


SCRAPE_CONFIG_FILENAME = "scrape_config.json"
scrape_config_file_path = os.path.join(os.getcwd(), SCRAPE_CONFIG_FILENAME)


def read_scrape_config() -> None:
    try:
        with open(scrape_config_file_path, "r", encoding="utf-8") as f:
            ScrapeConfig.from_dict(orjson.loads(f.read()))
    except FileNotFoundError:
        if questionary.confirm("未找到配置文件, 是否使用默认配置并生成文件?").ask():
            write_scrape_config()
        else:
            sys.exit()
    except orjson.JSONDecodeError:
        if questionary.confirm("配置文件格式错误导致解析失败, 是否使用默认配置并生成文件?").ask():
            write_scrape_config()
        else:
            sys.exit()
    except ValueError as err:
        if questionary.confirm(f"配置变量错误: {str(err)}, 是否使用默认配置并生成文件?").ask():
            write_scrape_config()
        else:
            sys.exit()


def write_scrape_config() -> None:
    with open(scrape_config_file_path, "w", encoding="utf-8") as f:
        f.write(orjson.dumps(ScrapeConfig.to_dict(), option=orjson.OPT_INDENT_2).decode("utf-8"))


def set_scrape_config() -> None:
    set_scrape_config_choice = [
        questionary.Choice(
            f"1. 头像保存模式({ScrapeConfigKeysEnum.DOWNLOAD_USER_AVATAR_MODE.value})",
            ScrapeConfigKeysEnum.DOWNLOAD_USER_AVATAR_MODE,
        ),
        questionary.Choice(
            f"2. 是否爬取转发的原帖({ScrapeConfigKeysEnum.SCRAPE_SHARE_ORIGIN.value})",
            ScrapeConfigKeysEnum.SCRAPE_SHARE_ORIGIN,
        ),
        questionary.Choice(
            f"3. 是否更新转发的原帖({ScrapeConfigKeysEnum.UPDATE_SHARE_ORIGIN.value})",
            ScrapeConfigKeysEnum.UPDATE_SHARE_ORIGIN,
        ),
        questionary.Choice(
            "4. 退出",
            "exit",
        ),
    ]
    while True:
        scrape_config_key = questionary.select("选择配置项", choices=set_scrape_config_choice).ask()
        if ScrapeConfigKeysEnum.DOWNLOAD_USER_AVATAR_MODE == scrape_config_key:
            download_user_avatar_mode_choices = [
                questionary.Choice(
                    f"1. 不保存({DownloadUserAvatarModeEnum.NONE.value})", DownloadUserAvatarModeEnum.NONE
                ),
                questionary.Choice(
                    f"2. 保存低清({DownloadUserAvatarModeEnum.LOW.value})", DownloadUserAvatarModeEnum.LOW
                ),
                questionary.Choice(
                    f"3. 保存高清({DownloadUserAvatarModeEnum.HIGH.value})", DownloadUserAvatarModeEnum.HIGH
                ),
            ]
            download_user_avatar_mode = questionary.select(
                "选择头像保存模式", choices=download_user_avatar_mode_choices
            ).ask()
            ScrapeConfig.DOWNLOAD_USER_AVATAR_MODE = download_user_avatar_mode.value
            write_scrape_config()
        elif ScrapeConfigKeysEnum.SCRAPE_SHARE_ORIGIN == scrape_config_key:
            scrape_share_origin = questionary.confirm("是否爬取转发的原帖?").ask()
            ScrapeConfig.SCRAPE_SHARE_ORIGIN = scrape_share_origin
            write_scrape_config()
        elif ScrapeConfigKeysEnum.UPDATE_SHARE_ORIGIN == scrape_config_key:
            update_share_origin = questionary.confirm("是否更新转发的原帖?").ask()
            ScrapeConfig.UPDATE_SHARE_ORIGIN = update_share_origin
            write_scrape_config()
        elif "exit" == scrape_config_key:
            break


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

        if ProgramFeatures.SCRAPE == selected_features:
            read_tieba_auth()
            read_scrape_config()
            tid = int(questionary.text("请输入要爬取的帖子的tid: ").ask())
            asyncio.run(scrape(tid))
        elif ProgramFeatures.SCRAPE_UPDATE == selected_features:
            read_tieba_auth()
            read_scrape_config()
            path = input("请输入本地帖子数据的路径: ")
            asyncio.run(scrape_update(path))
        elif ProgramFeatures.EXPORT_TO_READABLE == selected_features:
            print(f"{PrintColor.RED}该功能尚未实现{PrintColor.RESET}")
        elif ProgramFeatures.MODIFY_SCRAPE_CONFIG == selected_features:
            set_scrape_config()


if __name__ == "__main__":
    main()
