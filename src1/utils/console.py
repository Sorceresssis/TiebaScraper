class ConsoleColor:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    RESET = "\033[0m"


class Console:
    COLOR_RED = "\033[31m"
    COLOR_GREEN = "\033[32m"

    # _FORMATTER = logging.Formatter("<{asctime}> [{levelname}] [{funcName}] {message}", "%Y-%m-%d %H:%M:%S", style="{")

    def log(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def success(self, msg):
        print(msg)


import time
# <2025-03-06 01:54:22> [WARN] [get_forum] (3, '该吧还未建立，去看看其他贴吧吧'). args=('pythoan',) kwargs={}
print(time.asctime(time.localtime(time.time())))
print(time.asctime().format("%Y-%m-%d %H:%M:%S"))
