from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any

from pojo.enums import DownloadUserAvatarModeType


class ScrapeConfigKeysEnum(Enum):
    DOWNLOAD_USER_AVATAR_MODE = "DOWNLOAD_USER_AVATAR_MODE"
    SCRAPE_SHARE_ORIGIN = "SCRAPE_SHARE_ORIGIN"
    UPDATE_SHARE_ORIGIN = "UPDATE_SHARE_ORIGIN"


class DownloadUserAvatarModeEnum(Enum):
    NONE = 0
    LOW = 1
    HIGH = 2


@dataclass
class ScrapeConfig:
    DOWNLOAD_USER_AVATAR_MODE: int = 2  # 头像下载模式，0: 不下载头像, 1: 下载低清头像, 2: 下载高清头像

    # ANCHOR 以下配置仅在使用 scrape 功能时生效

    SCRAPE_SHARE_ORIGIN: bool = True  # 如果该贴是转发贴，是否爬取原帖的内容

    # ANCHOR 以下配置仅在使用 scrape_update 功能时生效

    UPDATE_SHARE_ORIGIN: bool = True  # 如果该贴是转发贴，是否更新原帖的内容

    # UPDATE_USER_INFO # 对于已经存在的用户，是否更新用户的 nickname, sign, traffic 信息.不包含avatar.
    # TODO avatar 的更新非常特殊。因为 avatar包含低清和高清版。如果更新的下载模式不同，会出现很多无用数据(内容相同但是清晰度不同的图片)。

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> None:
        download_user_avatar_mode = data.get(ScrapeConfigKeysEnum.DOWNLOAD_USER_AVATAR_MODE.value, 2)
        if download_user_avatar_mode not in DownloadUserAvatarModeType:
            raise ValueError(
                f"{ScrapeConfigKeysEnum.DOWNLOAD_USER_AVATAR_MODE.value} 的值必须是 0, 1, 2 中的一个"
            )
        cls.DOWNLOAD_USER_AVATAR_MODE = download_user_avatar_mode

        scrape_share_origin = data.get(ScrapeConfigKeysEnum.SCRAPE_SHARE_ORIGIN.value, True)
        if scrape_share_origin not in [True, False]:
            raise ValueError(f"{ScrapeConfigKeysEnum.SCRAPE_SHARE_ORIGIN.value} 的值必须是 True 或 False")
        cls.SCRAPE_SHARE_ORIGIN = scrape_share_origin

        update_share_origin = data.get(ScrapeConfigKeysEnum.UPDATE_SHARE_ORIGIN.value, True)
        if update_share_origin not in [True, False]:
            raise ValueError(f"{ScrapeConfigKeysEnum.UPDATE_SHARE_ORIGIN.value} 的值必须是 True 或 False")
        cls.UPDATE_SHARE_ORIGIN = update_share_origin

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        return {
            ScrapeConfigKeysEnum.DOWNLOAD_USER_AVATAR_MODE.value: cls.DOWNLOAD_USER_AVATAR_MODE,
            ScrapeConfigKeysEnum.SCRAPE_SHARE_ORIGIN.value: cls.SCRAPE_SHARE_ORIGIN,
            ScrapeConfigKeysEnum.UPDATE_SHARE_ORIGIN.value: cls.UPDATE_SHARE_ORIGIN,
        }
