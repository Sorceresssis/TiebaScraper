import os
import re
import time
from os import path


def sanitize_filename(filename: str) -> str:
    """
    去除文件名中的非法字符，并返回新的文件名
    要注意, 返回的可能是空字符串
    """

    invalid_chars = r'[<>:"/\\|?*]'
    sanitized_filename = re.sub(invalid_chars, "", filename)
    return sanitized_filename


def get_timestamp() -> int:
    timestamp = int(time.time() * 1000000)
    return timestamp


class ScrapeDataPathBuilder:
    DATA_FOLDER_NAME = "scraped_data"

    def __init__(self, item_dir) -> None:
        self.item_dir = item_dir

    @classmethod
    def get_instance_scrape(cls, forum_name: str, tid: int, title: str) -> "ScrapeDataPathBuilder":
        item_dir = path.join(
            path.join(os.getcwd(), cls.DATA_FOLDER_NAME),
            f"[{forum_name}吧][{tid}]{sanitize_filename(title)}_{get_timestamp()}",
        )
        os.makedirs(item_dir, exist_ok=True)
        return ScrapeDataPathBuilder(item_dir)

    @classmethod
    def get_instance_scrape_update(cls, source_path: str) -> "ScrapeDataPathBuilder":
        return ScrapeDataPathBuilder(source_path)

    def get_item_dir(self) -> str:
        return self.item_dir

    def get_scrape_info_path(self) -> str:
        return path.join(self.item_dir, "scrape_info.json")

    def get_thread_dir(self, tid: int) -> str:
        return path.join(self.item_dir, "threads", f"{tid}")

    def get_scrape_log_path(self, tid: int) -> str:
        return path.join(self.item_dir, "threads", f"{tid}", "scrape.log")

    def get_content_db_path(self, tid: int):
        return path.join(self.item_dir, "threads", f"{tid}", "content.db")

    def get_forum_info_path(self, tid) -> str:
        return path.join(self.item_dir, "threads", f"{tid}", "forum.json")

    def get_forum_avatar_dir(self, tid: int) -> str:
        return path.join(self.item_dir, "threads", f"{tid}", "forum_avatar")

    def get_thread_info_path(self, tid) -> str:
        return path.join(self.item_dir, "threads", f"{tid}", "thread.json")

    def get_user_avatar_dir(self, tid: int):
        avatar_dir = path.join(self.item_dir, "threads", f"{tid}", "user_avatar")
        os.makedirs(avatar_dir, exist_ok=True)
        return avatar_dir

    def get_post_image_dir(self, tid: int):
        image_dir = path.join(
            self.item_dir, "threads", f"{tid}", "post_assets", "images"
        )
        os.makedirs(image_dir, exist_ok=True)
        return image_dir

    def get_post_video_dir(self, tid: int):
        video_dir = path.join(
            self.item_dir, "threads", f"{tid}", "post_assets", "videos"
        )
        os.makedirs(video_dir, exist_ok=True)
        return video_dir

    def get_post_voice_dir(self, tid: int):
        voice_dir = path.join(
            self.item_dir, "threads", f"{tid}", "post_assets", "voices"
        )
        os.makedirs(voice_dir, exist_ok=True)
        return voice_dir

    @staticmethod
    def get_user_avatar_filename(portrait: str):
        return f"{portrait}"

    @staticmethod
    def get_post_image_filename(pid: int, idx: int):
        return f"p_{pid}_{idx}-{get_timestamp()}"

    @staticmethod
    def get_post_video_filename(pid: int, idx: int):
        return f"p_{pid}_{idx}-{get_timestamp()}"

    @staticmethod
    def get_post_voice_filename(voice_hash: str):
        return f"p_{voice_hash}"
