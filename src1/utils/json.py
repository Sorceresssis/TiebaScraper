import orjson


def json_loads(s: str) -> dict:
    return orjson.loads(s)


def json_loads_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json_loads(f.read())


def json_dumps(d: dict) -> str:
    return orjson.dumps(d, option=orjson.OPT_APPEND_NEWLINE).decode()


def json_dumps_file(d: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(json_dumps(d))
