import scrape_config

from pojo.enums import DownloadUserAvatarModeType


def check_scrape_config():
    if scrape_config.DOWNLOAD_USER_AVATAR_MODE not in DownloadUserAvatarModeType:
        raise Exception("DOWNLOAD_USER_AVATAR_MODE 配置错误")

    if scrape_config.SCRAPE_SHARE_ORIGIN not in [True, False]:
        raise Exception("SCRAPE_SHARE_ORIGIN 配置错误")

    if scrape_config.UPDATE_FORUM_AVATAR_ON_UPDATE not in [True, False]:
        raise Exception("UPDATE_FORUM_AVATAR_ON_UPDATE 配置错误")


def initial_checks():
    check_scrape_config()
