from dataclasses import dataclass, field

from typing import Optional


class ThreadStatus:
    NORMAL = 0
    DELETED = 1


@dataclass
class VoteOption:
    text: str = field(default="")
    vote_num: int = field(default=0)


@dataclass
class VoteInfo:
    title: str = field(default="")
    is_multi: bool = field(default=False)
    total_vote: int = field(default=0)
    total_user: int = field(default=0)
    options: list[VoteOption] = field(default_factory=list)


@dataclass
class ThreadInfo:
    id: int
    title: str
    forum_id: int
    forum_name: str
    post_id: int
    user_id: int
    type: int
    is_share: bool
    is_help: bool
    vote_info: VoteInfo
    share_origin: int
    view_num: int
    reply_num: int
    share_num: int
    agree: int
    disagree: int
    create_time: int

    status: Optional[int] = field(default=ThreadStatus.NORMAL)  # (v1.3.1)新增. 0 正常 1 可能已被屏蔽或删除
