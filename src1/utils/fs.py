import re


def sanitize_filename(filename: str) -> str:
    """
    去除文件名中的非法字符，并返回新的文件名
    要注意, 返回的可能是空字符串
    """

    invalid_chars = r'[<>:"/\\|?*]'
    sanitized_filename = re.sub(invalid_chars, "", filename)
    return sanitized_filename
