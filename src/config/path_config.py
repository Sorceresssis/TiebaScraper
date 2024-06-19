import os
from os import path
import time
from utils.fs import sanitize_filename


def unique_timestamp() -> int:
    # 睡眠一毫秒
    time.sleep(0.001)
    # 获取当前时间的毫秒时间戳
    timestamp = int(time.time() * 1000)
    return timestamp


class ScrapedPathConstructor:
    # 存放在工作目录下的scraped_data
    base = path.join(os.getcwd(), "scraped_data")

    def __init__(self, forum_name: str, tid: int, ttitle: str) -> None:
        self.scraped_data_dir = path.join(
            self.base,
            f"[{forum_name}吧][{tid}]{sanitize_filename(ttitle)}_{unique_timestamp()}",
        )
        os.makedirs(self.scraped_data_dir, exist_ok=True)

    def get_scraped_data_dir(self) -> str:
        return self.scraped_data_dir

    def get_scrape_log_path(self):
        return path.join(self.scraped_data_dir, "scrape.log")

    def get_scraper_info_path(self):
        return path.join(self.scraped_data_dir, "scrape_info.json")

    def get_thread_dir(self, tid: int):
        return path.join(self.scraped_data_dir, "threads", f"{tid}")

    def get_content_db_path(self, tid: int):
        return path.join(self.scraped_data_dir, "threads", f"{tid}", "content.db")

    def get_forum_info_path(self, tid: int):
        return path.join(self.scraped_data_dir, "threads", f"{tid}", "forum.json")

    def get_forum_avatar_dir(self, tid: int):
        return path.join(self.scraped_data_dir, "threads", f"{tid}", "forum_avatar")

    def get_thread_info_path(self, tid: int):
        return path.join(self.scraped_data_dir, "threads", f"{tid}", "thread.json")

    def get_user_avatar_dir(self, tid: int):
        """
        存放用户头像的文件夹路径, 运行时会自动创建文件夹
        """
        dir = path.join(self.scraped_data_dir, "threads", f"{tid}", "user_avatar")
        os.makedirs(dir, exist_ok=True)
        return dir

    def get_user_avatar_filename(self, uid: int):
        return f"u_{uid}_{unique_timestamp()}"

    def get_post_image_dir(self, tid: int):
        dir = path.join(
            self.scraped_data_dir, "threads", f"{tid}", "post_assets", "images"
        )
        os.makedirs(dir, exist_ok=True)
        return dir

    def get_post_video_dir(self, tid: int):
        dir = path.join(
            self.scraped_data_dir, "threads", f"{tid}", "post_assets", "videos"
        )
        os.makedirs(dir, exist_ok=True)
        return dir

    def get_post_voice_dir(self, tid: int):
        dir = path.join(
            self.scraped_data_dir, "threads", f"{tid}", "post_assets", "voices"
        )
        os.makedirs(dir, exist_ok=True)
        return dir

    def get_post_image_filename(self, pid: int):
        return f"p_{pid}_{unique_timestamp()}"

    def get_post_video_filename(self, pid: int):
        return f"p_{pid}_{unique_timestamp()}"

    def get_post_voice_filename(self, pid: int):
        return f"p_{pid}_{unique_timestamp()}"
