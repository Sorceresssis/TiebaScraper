from dataclasses import dataclass
from typing import Dict, Any, List


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

    # ONLY_APPLY_UPDATE_CONFIG_TO_NEW_BATCHES: bool = True

    # UPDATE_USER_INFO: bool = False
    """ 对于已经存在的用户，是否更新用户的 nickname, sign, traffic 信息.不包含avatar. """

    # TODO avatar 的更新非常特殊。因为 avatar包含低清和高清版。如果更新的下载模式不同，会出现很多无用数据(内容相同但是清晰度不同的图片)。

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> None:
        cls.POST_FILTER_TYPE = check_config_value(
            data,
            ScrapeConfigKeys.POST_FILTER_TYPE,
            [
                PostFilterType.ALL,
                PostFilterType.AUTHOR_POSTS_WITH_SUBPOSTS,
                PostFilterType.AUTHOR_POSTS_WITH_AUTHOR_SUBPOSTS,
                PostFilterType.AUTHOR_AND_REPLIED_POSTS_WITH_SUBPOSTS,
                PostFilterType.AUTHOR_AND_REPLIED_POSTS_WITH_AUTHOR_SUBPOSTS,
            ],
        )

        cls.DOWNLOAD_USER_AVATAR_MODE = check_config_value(
            data,
            ScrapeConfigKeys.DOWNLOAD_USER_AVATAR_MODE,
            [
                DownloadUserAvatarMode.NONE,
                DownloadUserAvatarMode.LOW,
                DownloadUserAvatarMode.HIGH,
            ],
        )

        cls.SCRAPE_SHARE_ORIGIN = check_config_value(
            data,
            ScrapeConfigKeys.SCRAPE_SHARE_ORIGIN,
            [True, False],
        )

        cls.UPDATE_SHARE_ORIGIN = check_config_value(
            data,
            ScrapeConfigKeys.UPDATE_SHARE_ORIGIN,
            [True, False],
        )

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        return {
            ScrapeConfigKeys.POST_FILTER_TYPE: cls.POST_FILTER_TYPE,
            ScrapeConfigKeys.DOWNLOAD_USER_AVATAR_MODE: cls.DOWNLOAD_USER_AVATAR_MODE,
            ScrapeConfigKeys.SCRAPE_SHARE_ORIGIN: cls.SCRAPE_SHARE_ORIGIN,
            ScrapeConfigKeys.UPDATE_SHARE_ORIGIN: cls.UPDATE_SHARE_ORIGIN,
        }


def check_config_value(data: Any, object_key: str, legal_values: List[Any]) -> Any:
    object_value = data.get(object_key)

    if object_value not in legal_values:
        raise ValueError(f"{object_key} 的值必须是 {legal_values} 中的一个")

    return object_value
