from pojo.enums import DownloadUserAvatarModeType
from scrape_config import ScrapeConfig


def get_user_avatar_base_url() -> str:
    if DownloadUserAvatarModeType.LOW == ScrapeConfig.DOWNLOAD_USER_AVATAR_MODE:
        return "http://tb.himg.baidu.com/sys/portrait/item/"
    elif DownloadUserAvatarModeType.HIGH == ScrapeConfig.DOWNLOAD_USER_AVATAR_MODE:
        return "https://himg.bdimg.com/sys/portraith/item/"
    elif DownloadUserAvatarModeType.NONE == ScrapeConfig.DOWNLOAD_USER_AVATAR_MODE:
        return ""
    else:
        raise Exception("未知的头像下载类型")


class TiebaApi:
    USER_AVATAR_BASE_URL = get_user_avatar_base_url()

    @classmethod
    def get_user_avatar_url(cls, portrait: str) -> str:
        return cls.USER_AVATAR_BASE_URL + portrait

    @classmethod
    def get_voice_url(cls, voice_hash: str) -> str:
        return f"https://tiebac.baidu.com/c/p/voice?voice_md5={voice_hash}&play_from=pb_voice_play"
