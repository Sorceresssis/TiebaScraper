from dataclasses import dataclass


@dataclass
class TiebaOriginSrcEntity:
    filename: str
    content_frag_type: int
    origin_src: str
