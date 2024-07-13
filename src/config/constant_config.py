from tieba_property import DOWNLOAD_USER_AVATAR
from enum import IntEnum


class DownlodUserAvatarType(IntEnum):
    NONE = 0  # 不下载
    LOW = 1  # 低清
    HIGH = 2  # 高清


def get_user_avatar_base_url() -> str:
    if DownlodUserAvatarType.LOW == DOWNLOAD_USER_AVATAR:
        return "http://tb.himg.baidu.com/sys/portrait/item/"
    elif DownlodUserAvatarType.HIGH == DOWNLOAD_USER_AVATAR:
        return "https://himg.bdimg.com/sys/portraith/item/"
    elif DownlodUserAvatarType.NONE == DOWNLOAD_USER_AVATAR:
        return ""
    else:
        raise Exception("未知的头像下载类型")


USER_AVATAR_BASE_URL = get_user_avatar_base_url()


def get_user_avatar_url(portrait: str) -> str:
    return USER_AVATAR_BASE_URL + portrait


def get_voice_url(hash: str) -> str:
    return (
        f"https://tiebac.baidu.com/c/p/voice?voice_md5={ hash }&play_from=pb_voice_play"
    )
