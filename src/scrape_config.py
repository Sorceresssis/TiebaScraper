from dataclasses import dataclass
from typing import Dict, Any


class ScrapeConfigKeys:
    DOWNLOAD_USER_AVATAR_MODE = "DOWNLOAD_USER_AVATAR_MODE"
    SCRAPE_SHARE_ORIGIN = "SCRAPE_SHARE_ORIGIN"
    UPDATE_SHARE_ORIGIN = "UPDATE_SHARE_ORIGIN"
    POST_FILTER_TYPE = "POST_FILTER_TYPE"


class DownloadUserAvatarMode:
    NONE = "none"  # 不下载头像
    LOW = "low"  # 低清头像
    HIGH = "high"  # 高清头像


class PostFilterType:
    ALL = "all"
    """ '所有的 post' + 'post 下的所有 subpost' """
    AUTHOR_POSTS_WITH_SUBPOSTS = "author_posts_with_subposts"
    """ 'thread_author 的 post' + 'post 下的所有 subpost' """
    AUTHOR_POSTS_WITH_AUTHOR_SUBPOSTS = "author_posts_with_author_subposts"
    """ 'thread_author 的 post' + 'post 下 thread_author 的 subpost' """
    AUTHOR_AND_REPLIED_POSTS_WITH_SUBPOSTS = "author_and_replied_posts_with_subposts"
    """ 'thread_author 的 post 和 thread_author 回复过的 post' + 'post 下所有的 subpost' """
    AUTHOR_AND_REPLIED_POSTS_WITH_AUTHOR_SUBPOSTS = "author_and_replied_posts_with_author_subposts"
    """ 'thread_author 的 post 和 thread_author 回复过的 post' + 'post 下 thread_author 的 subpost' """


@dataclass
class ScrapeConfig:
    DOWNLOAD_USER_AVATAR_MODE: str = DownloadUserAvatarMode.HIGH

    POST_FILTER_TYPE: str = PostFilterType.ALL

    # ANCHOR 以下配置仅在使用 scrape 功能时生效

    SCRAPE_SHARE_ORIGIN: bool = True  # 如果该贴是转发贴，是否爬取原帖的内容

    # ANCHOR 以下配置仅在使用 scrape_update 功能时生效

    UPDATE_SHARE_ORIGIN: bool = True  # 如果该贴是转发贴，是否更新原帖的内容

    UPDATE_USER_INFO: bool = False
    """ 对于已经存在的用户，是否更新用户的 nickname, sign, traffic 信息.不包含avatar. """

    # TODO avatar 的更新非常特殊。因为 avatar包含低清和高清版。如果更新的下载模式不同，会出现很多无用数据(内容相同但是清晰度不同的图片)。

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> None:
        download_user_avatar_mode = data.get(ScrapeConfigKeys.DOWNLOAD_USER_AVATAR_MODE)
        if download_user_avatar_mode not in [
            DownloadUserAvatarMode.NONE,
            DownloadUserAvatarMode.LOW,
            DownloadUserAvatarMode.HIGH,
        ]:
            raise ValueError(
                f"{ScrapeConfigKeys.DOWNLOAD_USER_AVATAR_MODE} 的值必须是 {DownloadUserAvatarMode.NONE}, {DownloadUserAvatarMode.LOW}, {DownloadUserAvatarMode.HIGH} 中的一个"
            )
        cls.DOWNLOAD_USER_AVATAR_MODE = download_user_avatar_mode

        scrape_share_origin = data.get(ScrapeConfigKeys.SCRAPE_SHARE_ORIGIN)
        if scrape_share_origin not in [True, False]:
            raise ValueError(f"{ScrapeConfigKeys.SCRAPE_SHARE_ORIGIN} 的值必须是 True 或 False")
        cls.SCRAPE_SHARE_ORIGIN = scrape_share_origin

        update_share_origin = data.get(ScrapeConfigKeys.UPDATE_SHARE_ORIGIN)
        if update_share_origin not in [True, False]:
            raise ValueError(f"{ScrapeConfigKeys.UPDATE_SHARE_ORIGIN} 的值必须是 True 或 False")
        cls.UPDATE_SHARE_ORIGIN = update_share_origin

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        return {
            ScrapeConfigKeys.POST_FILTER_TYPE: cls.POST_FILTER_TYPE,
            ScrapeConfigKeys.DOWNLOAD_USER_AVATAR_MODE: cls.DOWNLOAD_USER_AVATAR_MODE,
            ScrapeConfigKeys.SCRAPE_SHARE_ORIGIN: cls.SCRAPE_SHARE_ORIGIN,
            ScrapeConfigKeys.UPDATE_SHARE_ORIGIN: cls.UPDATE_SHARE_ORIGIN,
        }

    @staticmethod
    def find_diff_config(old_config: dict, new_config: dict):
        pass
