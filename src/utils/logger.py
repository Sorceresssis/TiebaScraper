import logging

from utils.msg_printer import generate_affiliation_str


class ScrapeLogger(logging.Logger):
    def __init__(self, log_path: str) -> None:
        super().__init__("ScrapeNewLogger")

        # 创建 FileHandler 将日志记录到文件
        file_handler = logging.FileHandler(log_path, encoding="utf-8")

        # 创建日志格式
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(module)s.%(filename)s - %(message)s"
            )
        )

        self.addHandler(file_handler)


def generate_scrape_logger_msg(
        msg: str = "", label: str | None = None, affiliations: list = []
):
    return "".join(
        [
            "" if label is None else f"{label}",
            f" - {generate_affiliation_str(affiliations)}" if len(affiliations) else "",
            f" - {msg}" if len(msg) else "",
        ]
    )
