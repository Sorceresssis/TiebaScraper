import os
import re
import requests


def sanitize_filename(filename: str) -> str:
    # 定义不能作为文件名的字符
    invalid_chars = r'[\/:*?"<>|]'
    # 替换这些字符为空字符
    sanitized_filename = re.sub(invalid_chars, "", filename)
    return sanitized_filename


def download_file(
    url, save_dir, filename_without_extname, extname=None, retries=3
) -> tuple[str, str]:
    """
    下载文件并保存到指定目录，根据 Content-Type 设置文件扩展名。

    :param url: 文件的 URL
    :param save_dir: 保存文件的目录
    :param filename: 文件名（不包含扩展名）
    :param extname: 扩展名（如果不指定，则根据 Content-Type 自动确定）
    :param retries: 下载错误时的重试次数，默认值为3

    :return: 保存的文件名和路径
    """

    attempt = 0
    while attempt < retries:
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()

                # 获取 Content-Type 并确定扩展名
                if extname is None:
                    content_type = r.headers.get("Content-Type")
                    if content_type:
                        extname = content_type.split("/")[1]
                    else:
                        extname = os.path.splitext(url)[1].split("?")[0]

                # 构建完整的文件路径
                filename = f"{filename_without_extname}.{extname}"
                file_path = os.path.join(save_dir, filename)

                # 确保保存目录存在
                os.makedirs(save_dir, exist_ok=True)

                # 保存文件
                with open(file_path, "wb") as file:
                    for chunk in r.iter_content(chunk_size=8192):
                        file.write(chunk)

                return (filename, file_path)
        except requests.RequestException as e:
            attempt += 1
            print(f"Download failed: {e}. Retrying {attempt}/{retries}...")

    raise Exception(f"Failed to download file after {retries} attempts.")
