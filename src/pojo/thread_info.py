from dataclasses import dataclass


@dataclass
class VoteOption:
    text: str
    vote_num: int


@dataclass
class VoteInfo:
    title: str
    is_multi: bool
    total_vote: int
    total_user: int
    options: list[VoteOption]


@dataclass
class ThreadInfo:
    id: int
    title: str
    forum_id: int
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
