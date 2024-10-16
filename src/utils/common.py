from typing import Any

import orjson


def counter_gen(start=0, step=1):
    while True:
        start += step
        new_values = yield start
        if new_values is not None:
            step = new_values[1]
            start = new_values[0] - step


def json_dumps(data: Any, to_format: bool = True) -> str:
    if to_format:
        return orjson.dumps(data, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS | orjson.OPT_NON_STR_KEYS).decode(
            "utf-8")
    else:
        return orjson.dumps(data).decode("utf-8")
