class PrintColor:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    RESET = "\033[0m"


def generate_affiliation_str(affiliations: list):
    if len(affiliations) % 2 != 0:
        raise ValueError("The affiliations list must contain an even number of elements.")

    formatted_pairs = [f"{affiliations[i]}:{affiliations[i + 1]}" for i in range(0, len(affiliations), 2)]
    result = f"< {', '.join(formatted_pairs)} >"
    return result


class MsgPrinter:
    STEP_MARK_LABEL = "---------------- Step Mark ----------------"
    TIPS_LABEL = "---------------- Tips ----------------"

    @classmethod
    def print_error(cls, msg: str = "", label: str | None = None, affiliations: list = []):
        print(
            f"{PrintColor.RED}ERROR{PrintColor.RESET}",
            (f" - {PrintColor.BLUE}{label}{PrintColor.RESET}" if label is not None else ""),
            f" - {generate_affiliation_str(affiliations)}" if len(affiliations) else "",
            f" - {msg}" if len(msg) else "",
            sep="",
        )

    @classmethod
    def print_info(cls, msg: str = "", label: str | None = None, affiliations: list = []):
        print(
            f"{PrintColor.BLUE}INFO{PrintColor.RESET}",
            (f" - {PrintColor.BLUE}{label}{PrintColor.RESET}" if label is not None else ""),
            f" - {generate_affiliation_str(affiliations)}" if len(affiliations) else "",
            f" - {msg}" if len(msg) else "",
            sep="",
        )

    @classmethod
    def print_success(cls, msg: str = "", label: str | None = None, affiliations: list = []):
        print(
            f"{PrintColor.GREEN}SUCCESS{PrintColor.RESET}",
            (f" - {PrintColor.BLUE}{label}{PrintColor.RESET}" if label is not None else ""),
            f" - {generate_affiliation_str(affiliations)}" if len(affiliations) else "",
            f" - {msg}" if len(msg) else "",
            sep="",
        )

    @classmethod
    def print_warning(cls, msg: str = "", label: str | None = None, affiliations: list = []):
        print(
            f"{PrintColor.YELLOW}WARNING{PrintColor.RESET}",
            (f" - {PrintColor.BLUE}{label}{PrintColor.RESET}" if label is not None else ""),
            f" - {generate_affiliation_str(affiliations)}" if len(affiliations) else "",
            f" - {msg}" if len(msg) else "",
            sep="",
        )

    @classmethod
    def print_step_mark(cls, msg: str = "", affiliations: list = []):
        print(
            f"{PrintColor.BLUE}INFO{PrintColor.RESET}",
            f" - {PrintColor.BLUE}{cls.STEP_MARK_LABEL}{PrintColor.RESET}",
            f" {generate_affiliation_str(affiliations)}" if len(affiliations) else "",
            f" {msg}" if len(msg) else "",
            sep="",
        )

    @classmethod
    def print_tip(cls, msg: str = "", affiliations: list = []):
        print(
            f"{PrintColor.BLUE}INFO{PrintColor.RESET}",
            f" - {PrintColor.BLUE}{cls.TIPS_LABEL}{PrintColor.RESET}",
            (f" {generate_affiliation_str(affiliations)} - " if len(affiliations) else " - "),
            f"{msg}" if len(msg) else "",
            sep="",
        )
