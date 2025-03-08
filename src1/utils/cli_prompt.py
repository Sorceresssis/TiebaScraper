from typing import Sequence, Any

from prompt_toolkit.styles import Style

import questionary

from questionary import Choice

WarningStyle = Style([
    ('qmark', 'fg:red bold'),  # 问号用红色加粗表示警告
    ('question', 'fg:yellow bold'),  # 问题文本为黄色加粗，提升警示感
    ('answer', 'fg:white bold'),  # 回答的文本为白色加粗
    ('selected', 'fg:yellow bold'),  # 被选中的选项为黄色加粗
])

SuccessStyle = Style([
    ('qmark', 'fg:green bold'),
    ('question', 'fg:green bold'),
    ('answer', 'fg:cyan bold'),
    ('selected', 'fg:green bold'),
])

ErrorStyle = Style([
    ('qmark', 'fg:red bold'),
    ('question', 'fg:red bold'),
    ('answer', 'fg:white bold'),
    ('selected', 'fg:red bold'),
])

InfoStyle = Style([
    ('qmark', 'fg:blue bold'),
    ('question', 'fg:white bold'),
    ('answer', 'fg:blue bold'),
    ('selected', 'fg:blue bold'),
])

PromptStyle = Style([
    ('qmark', 'fg:cyan bold'),
    ('question', 'fg:white bold'),
    ('answer', 'fg:cyan bold'),
    ('selected', 'fg:cyan bold'),
])
SELECT_STYLE = Style([

])

CONFIRM_STYLE = Style([])

prompt_style = Style([
    # 问题标记（?）的样式
    ('qmark', 'fg:cyan bold'),
    # 问题文本的样式
    ('question', 'fg:white bold'),
    # 回答的样式
    ('answer', 'fg:cyan bold'),
    # 选中项的样式
    ('selected', 'fg:cyan bold'),
    # 指示符（>）的样式
    ('pointer', 'fg:cyan bold'),
    # 未选中项的样式
    ('text', ''),
    # 分隔线的样式
    ('separator', 'fg:#ffffff'),
])


def select(message: str, choices: Sequence[str | questionary.Choice | dict[str, Any]]):
    return questionary.select(
        message,
        choices=choices,
        style=SELECT_STYLE
    )


def confirm(message: str, ):
    return questionary.confirm(
        message,
        style=CONFIRM_STYLE
    )


def text(message: str, ):
    return questionary.text(
        message,
        style=PromptStyle
    )


__all__ = [
    select,
    confirm,
    text,
    Choice
]
