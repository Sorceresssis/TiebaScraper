from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class TiebaAuth:
    BDUSS: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> None:
        cls.BDUSS = data.get("BDUSS", "")
