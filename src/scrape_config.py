from dataclasses import dataclass
from typing import Dict, Any

from pojo.enums import DownloadUserAvatarModeType


@dataclass
class ScrapeConfig:
    DOWNLOAD_USER_AVATAR_MODE: int = 2  # 头像下载模式，0: 不下载头像, 1: 下载低清头像, 2: 下载高清头像

    SCRAPE_SHARE_ORIGIN: bool = True  # 如果该贴是转发贴，是否爬取原帖的内容

    # 以下配置仅在使用 scrape_update 功能时生效

    UPDATE_FORUM_AVATAR_ON_UPDATE: bool = True  # 更新帖子时，是否更新论坛头像

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> None:
        download_user_avatar_mode = data.get("DOWNLOAD_USER_AVATAR_MODE", 2)
        if download_user_avatar_mode not in DownloadUserAvatarModeType:
            raise ValueError("DOWNLOAD_USER_AVATAR_MODE 的值必须是 0, 1, 2 中的一个")
        cls.DOWNLOAD_USER_AVATAR_MODE = download_user_avatar_mode

        scrape_share_origin = data.get("SCRAPE_SHARE_ORIGIN", True)
        if scrape_share_origin not in [True, False]:
            raise ValueError("SCRAPE_SHARE_ORIGIN 的值必须是 True 或 False")
        cls.SCRAPE_SHARE_ORIGIN = scrape_share_origin

        update_forum_avatar_on_update = data.get("UPDATE_FORUM_AVATAR_ON_UPDATE", True)
        if update_forum_avatar_on_update not in [True, False]:
            raise ValueError("UPDATE_FORUM_AVATAR_ON_UPDATE 的值必须是 True 或 False")
        cls.UPDATE_FORUM_AVATAR_ON_UPDATE = update_forum_avatar_on_update
