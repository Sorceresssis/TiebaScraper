from dataclasses import dataclass, asdict


@dataclass
class PostEntity:
    id: int
    contents: str
    floor: int  # 楼和楼中楼一样
    user_id: int
    agree: int
    disagree: int
    create_time: int
    is_thread_author: bool
    sign: str = ""  # 楼独有, 小尾巴
    reply_num: int = 0  # 楼独有, 回复数
    # 楼中楼独有, 区分楼和楼中楼的唯一标识 where parent_id = 0
    parent_id: int = 0
    # 楼中楼独有, 也不是所有的楼中楼都有这个字段, 对应的是楼中楼的作者user_id, 不是post_id
    reply_to_id: int = 0
