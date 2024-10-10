from enum import IntEnum, auto


class ProgramFeatures(IntEnum):
    SCRAPE = auto()
    SCRAPE_UPDATE = auto()
    EXPORT_TO_READABLE = auto()
    MODIFY_SCRAPE_CONFIG = auto()


class DownloadUserAvatarModeType(IntEnum):
    NONE = 0  # 不下载
    LOW = 1  # 低清
    HIGH = 2  # 高清
