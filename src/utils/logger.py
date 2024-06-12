import logging


class ScrapeLogger(logging.Logger):
    def __init__(self, log_path: str) -> None:
        super().__init__("ScrapeLogger")

        # 创建 FileHandler 将日志记录到文件
        file_handler = logging.FileHandler(log_path, encoding="utf-8")

        # 创建日志格式
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(module)s.%(filename)s - func:%(funcName)s - %(message)s"
            )
        )

        self.addHandler(file_handler)
