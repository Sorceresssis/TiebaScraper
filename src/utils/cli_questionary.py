from prompt_toolkit.styles import Style

WarningStyle = Style([
    ('qmark', 'fg:red bold'),  # 问号用红色加粗表示警告
    ('question', 'fg:yellow bold'),  # 问题文本为黄色加粗，提升警示感
    ('answer', 'fg:white bold'),  # 回答的文本为白色加粗
    ('selected', 'fg:yellow bold'),  # 被选中的选项为黄色加粗
])

SuccessStyle = Style([
    ('qmark', 'fg:green bold'),  # 问号用绿色加粗表示成功
    ('question', 'fg:green bold'),  # 问题文本为绿色加粗，正面提示
    ('answer', 'fg:cyan bold'),  # 回答的文本为青色加粗
    ('selected', 'fg:green bold'),  # 选中的选项为绿色加粗
])

ErrorStyle = Style([
    ('qmark', 'fg:red bold'),  # 问号用红色加粗表示错误
    ('question', 'fg:red bold'),  # 问题文本为红色加粗，提升错误提示感
    ('answer', 'fg:white bold'),  # 回答的文本为白色加粗
    ('selected', 'fg:red bold'),  # 被选中的选项为红色加粗
])

InfoStyle = Style([
    ('qmark', 'fg:blue bold'),  # 问号用蓝色加粗表示信息提示
    ('question', 'fg:white bold'),  # 问题文本为白色加粗，表示普通信息
    ('answer', 'fg:blue bold'),  # 回答的文本为蓝色加粗
    ('selected', 'fg:blue bold'),  # 被选中的选项为蓝色加粗
])

PromptStyle = Style([
    ('qmark', 'fg:cyan bold'),  # 问号用青色加粗表示轻松提示
    ('question', 'fg:white bold'),  # 问题文本为白色加粗，表示普通提示
    ('answer', 'fg:cyan bold'),  # 回答的文本为青色加粗
    ('selected', 'fg:cyan bold'),  # 被选中的选项为青色加粗
])
