from dataclasses import dataclass

from pojo.user_status import UserStatus


@dataclass
class UserEntity:
    id: int
    portrait: str | None = None
    username: str | None = None
    nickname: str = ""
    tieba_uid: int | None = None

    avatar: str | None = None
    glevel: int = 0
    gender: int = 0
    ip: str = ""
    is_vip: bool = False
    is_god: bool = False
    age: float = 0
    sign: str = ""
    post_num: int = 0
    agree_num: int = 0
    fan_num: int = 0
    follow_num: int = 0
    forum_num: int = 0

    level: int = 0
    is_bawu: bool = False
    status: int = UserStatus.ACTIVE

    completed: int = 0  # 0 | 1
    scrape_time: int = 0
