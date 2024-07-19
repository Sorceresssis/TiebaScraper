from enum import IntEnum

from scrape_config import DOWNLOAD_USER_AVATAR


class DownloadUserAvatarType(IntEnum):
    NONE = 0  # 不下载
    LOW = 1  # 低清
    HIGH = 2  # 高清


def get_user_avatar_base_url() -> str:
    if DownloadUserAvatarType.LOW == DOWNLOAD_USER_AVATAR:
        return "http://tb.himg.baidu.com/sys/portrait/item/"
    elif DownloadUserAvatarType.HIGH == DOWNLOAD_USER_AVATAR:
        return "https://himg.bdimg.com/sys/portraith/item/"
    elif DownloadUserAvatarType.NONE == DOWNLOAD_USER_AVATAR:
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
        return (
            f"https://tiebac.baidu.com/c/p/voice?voice_md5={voice_hash}&play_from=pb_voice_play"
        )
