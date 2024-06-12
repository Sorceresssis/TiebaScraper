from enum import IntEnum, auto


class UserStatus(IntEnum):
    ACTIVE = 0  # 正常
    DEACTIVATED = auto()  # 注销
