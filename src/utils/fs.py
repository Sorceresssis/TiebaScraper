import os
from typing import Any

import aiofiles
import aiohttp
import orjson


async def download_file(
        url, save_dir, filename_without_extname, extname=None, retries=3
) -> tuple[str, str]:
    """
    下载文件并保存到指定目录，根据 Content-Type 设置文件扩展名。

    :param url: 文件的 URL
    :param save_dir: 保存文件的目录
    :param filename_without_extname: 文件名（不包含扩展名）
    :param extname: 扩展名（如果不指定，则根据 Content-Type 自动确定）带上.
    :param retries: 下载错误时的重试次数，默认值为3

    :return: 保存的文件名和路径
    """
    attempt = 0

    while attempt < retries:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()  # 检查请求是否成功

                    if extname is None:
                        content_type = response.content_type

                        if content_type:
                            extname = content_type.split("/")[1]
                        else:
                            extname = os.path.splitext(url)[1].split("?")[0][1:]

                    filename = f"{filename_without_extname}.{extname}"
                    full_path = os.path.join(save_dir, filename)

                    os.makedirs(save_dir, exist_ok=True)
                    async with aiofiles.open(full_path, "wb") as file:
                        while True:
                            chunk = await response.content.read(8192)
                            if not chunk:
                                break
                            await file.write(chunk)

                    return filename, full_path

        except aiohttp.ClientError as e:
            attempt += 1

    raise Exception(f"Failed to download {url} after {retries} attempts")


def json_dumps(data: Any):
    return orjson.dumps(data, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS | orjson.OPT_NON_STR_KEYS).decode(
        "utf-8")
