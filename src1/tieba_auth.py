from typing import Dict, Any
import os
import utils.cli_prompt as cli_prompt

from utils.json import json_loads_file, json_dumps_file

TIEBA_AUTH_FILENAME = "tieba_auth.json"


class TiebaAuth:
    BDUSS: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> None:
        cls.BDUSS = data.get("BDUSS", "")

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        return {
            "BDUSS": cls.BDUSS,
        }

    @classmethod
    def load_tieba_auth(cls) -> None:
        tieba_auth_file_path = os.path.join(os.getcwd(), TIEBA_AUTH_FILENAME)

        try:
            json_loads_file(tieba_auth_file_path)
        except Exception:
            bduss = cli_prompt.text("未配置BDUSS, 请输入: ").ask()
            TiebaAuth.BDUSS = bduss
            json_dumps_file(TiebaAuth.to_dict(), tieba_auth_file_path)
