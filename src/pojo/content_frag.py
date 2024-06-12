from dataclasses import dataclass
from enum import IntEnum, auto


class ContentFragType(IntEnum):
    """
    text
    emojis
    imgs
    ats
    links
    tiebapluses
    video	视频碎片
    voice
    """

    TEXT = auto()
    EMOJI = auto()
    IMAGE = auto()
    AT = auto()
    LINK = auto()
    TIEBAPLUS = auto()
    VIDEO = auto()
    VOICE = auto()


@dataclass
class ContentFrag:
    type: int


@dataclass
class FragText(ContentFrag):
    text: str


@dataclass
class FragEmoji(ContentFrag):
    id: str
    desc: str


@dataclass
class FragImage(ContentFrag):
    filename: str
    tb_origin_src: str  # tieba 的原图链接
    origin_size: int  # 通常是0不知到有什么样
    show_width: int
    show_height: int
    hash: str


@dataclass
class FragAt(ContentFrag):
    text: str
    user_id: int


@dataclass
class FragLink(ContentFrag):
    text: str
    title: str
    raw_url: str


@dataclass
class FragTiebaPlus(ContentFrag):
    """
    贴吧plus广告碎片

    Attributes:
        text (str): 贴吧plus广告描述
        url (yarl.URL): 解析后的贴吧plus广告跳转链接
    """

    text: str = ""
    url: str = ""


@dataclass
class FragVideo(ContentFrag):
    filename: str
    cover_filename: str
    duration: int
    width: int
    height: int
    view_num: int

    tb_origin_src: str
    tb_origin_cover_src: str


@dataclass
class FragVoice(ContentFrag):
    md5: str
    duration: int
    tb_origin_src: str
