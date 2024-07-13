from dataclasses import dataclass


@dataclass
class UserEntity:
    id: int
    portrait: str
    username: str | None
    nickname: str
    avatar: str | None
    glevel: int
    gender: int
    ip: str
    is_vip: bool
    is_god: bool
    tieba_uid: int | None
    age: float
    sign: str
    post_num: int
    agree_num: int
    fan_num: int
    follow_num: int
    forum_num: int
    level: int
    is_bawu: bool
    status: int
