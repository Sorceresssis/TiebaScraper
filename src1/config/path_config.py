import os
from os import path
from ..utils.common import get_timestamp
from ..utils.fs import sanitize_filename

DATA_FOLDER_NAME = "scraped_data"


class ThreadDataPathBuilder:

    def __init__(self, item_dir):
        self.item_dir = item_dir

    @classmethod
    def from_scrape_thread(cls, f_name: str, t_id: int, t_title: str) -> "ThreadDataPathBuilder":
        item_dir = path.join(
            os.getcwd(),
            DATA_FOLDER_NAME,
            cls.gen_thread_data_folder_name(f_name, t_id, t_title),
        )
        os.makedirs(item_dir, exist_ok=True)
        return ThreadDataPathBuilder(item_dir)

    @classmethod
    def from_append_posts(cls, target_dir: str) -> "ThreadDataPathBuilder":
        return ThreadDataPathBuilder(target_dir)

    @classmethod
    def from_custom_dir(cls, custom_dir: str, f_name: str, t_id: int, t_title: str) -> "ThreadDataPathBuilder":
        item_dir = path.join(
            custom_dir,
            ThreadDataPathBuilder.gen_thread_data_folder_name(f_name, t_id, t_title),
        )
        os.makedirs(item_dir, exist_ok=True)
        return ThreadDataPathBuilder(item_dir)

    @staticmethod
    def gen_thread_data_folder_name(f_name: str, t_id: int, t_title: str) -> str:
        return f"[{f_name}吧][{t_id}]{sanitize_filename(t_title)}_{get_timestamp()}"

    def get_scrape_info_path(self) -> str:
        return path.join(self.item_dir, "scrape_info.json")

    def get_thread_dir(self, tid: int) -> str:
        return path.join(self.item_dir, "threads", str(tid))

    def get_scrape_log_path(self, tid: int, timestamp: int) -> str:
        return path.join(self.item_dir, "threads", str(tid), f"scrape.{timestamp}.log")

    def get_content_db_path(self, tid: int):
        return path.join(self.item_dir, "threads", str(tid), "content.db")

    def get_forum_info_path(self, tid) -> str:
        return path.join(self.item_dir, "threads", str(tid), "forum.json")

    def get_forum_avatar_dir(self, tid: int) -> str:
        return path.join(self.item_dir, "threads", str(tid), "forum_avatar")

    def get_thread_info_path(self, tid) -> str:
        return path.join(self.item_dir, "threads", str(tid), "thread.json")

    def get_user_avatar_dir(self, tid: int):
        avatar_dir = path.join(self.item_dir, "threads", str(tid), "user_avatar")
        os.makedirs(avatar_dir, exist_ok=True)
        return avatar_dir

    def get_post_assets_dir(self, tid: int) -> str:
        return path.join(self.item_dir, "threads", str(tid), "post_assets")

    def get_post_image_dir(self, tid: int):
        image_dir = path.join(self.item_dir, "threads", str(tid), "post_assets", "images")
        os.makedirs(image_dir, exist_ok=True)
        return image_dir

    def get_post_video_dir(self, tid: int):
        video_dir = path.join(self.item_dir, "threads", str(tid), "post_assets", "videos")
        os.makedirs(video_dir, exist_ok=True)
        return video_dir

    def get_post_voice_dir(self, tid: int):
        voice_dir = path.join(self.item_dir, "threads", str(tid), "post_assets", "voices")
        os.makedirs(voice_dir, exist_ok=True)
        return voice_dir

    @staticmethod
    def get_forum_small_avatar_filename(forum_name: str):
        return f"f_{forum_name}_small-avatar_{get_timestamp()}"

    @staticmethod
    def get_forum_small_avatar_filename_pattern():
        return rf".*small.*"

    @staticmethod
    def get_forum_origin_avatar_filename(forum_name: str):
        return f"f_{forum_name}_origin-avatar_{get_timestamp()}"

    @staticmethod
    def get_forum_origin_avatar_filename_pattern():
        return rf".*origin.*"

    @staticmethod
    def get_user_avatar_filename(portrait: str):
        return f"{portrait}_{get_timestamp()}"

    @staticmethod
    def get_user_avatar_filename_pattern(portrait: str):
        return rf".*{portrait}.*"

    @staticmethod
    def get_post_image_filename(pid: int, idx: int):
        return f"p_{pid}_{idx}_{get_timestamp()}"

    @staticmethod
    def get_post_video_filename(pid: int, idx: int):
        return f"p_{pid}_{idx}_{get_timestamp()}"

    @staticmethod
    def get_post_voice_filename(pid: int, idx: int, voice_hash: str):
        return f"p_{pid}_{idx}_{voice_hash}"

    @staticmethod
    def get_post_assets_filename_pattern(pid: int):
        return rf".*p_{pid}_.*"


class UserDataPathBuilder:

    def __init__(self, item_dir):
        self.item_dir = item_dir

    def get_user_threads_dir(self):
        return path.join(self.item_dir, "user_threads")

    @staticmethod
    def gen_user_folder_name(nickname: str, user_id: int, ) -> str:
        return f"{nickname}{"" if user_id == 0 else f"[{user_id}]"}_{get_timestamp()}"
