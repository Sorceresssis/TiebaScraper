def get_user_avatar_url(portrait: str) -> str:
    return f"https://himg.bdimg.com/sys/portraith/item/{portrait}"


def get_voice_url(hash: str) -> str:
    return (
        f"https://tiebac.baidu.com/c/p/voice?voice_md5={ hash }&play_from=pb_voice_play"
    )
