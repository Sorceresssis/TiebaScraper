from prompt_toolkit.styles import Style

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
