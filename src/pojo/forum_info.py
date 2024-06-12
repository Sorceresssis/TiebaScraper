from dataclasses import dataclass, field


@dataclass
class ForumInfo:
    """
    贴吧的信息

    Attributes:
        id (int): id
        name (str): 名称
        category (str): 分类
        subcategory (str): 子分类
        member_num (int): 成员数
        post_num (int): 帖子数
        thread_num (int): 主题数
        slogan (str): 标语
        small_avatar (str): 小头像
        origin_avatar (str): 原始头像
    """

    id: int
    name: str
    category: str
    subcategory: str
    member_num: int
    post_num: int
    thread_num: int
    slogan: str
    small_avatar: str
    origin_avatar: str
