# ScrapeConfig 爬取配置

## POST_FILTER_TYPE

对获取到的数据进行有选择性的保存，只对当前爬取批次有效。

| 值                                            | 说明                                                                                      |
| :-------------------------------------------- | ----------------------------------------------------------------------------------------- |
| all                                           | 所有的 post `+`  post 下的所有 subpost                                                    |
| author_posts_with_subposts                    | thread_author 的 post `+` post 下的所有 subpost                                           |
| author_posts_with_author_subposts             | thread_author 的 post `+` post 下的所有 subpost                                           |
| author_and_replied_posts_with_subposts        | thread_author 的 post 和 thread_author 回复过的 post `+` post 下所有的 subpost            |
| author_and_replied_posts_with_author_subposts | thread_author 的 post 和 thread_author 回复过的 post `+` post 下 thread_author 的 subpost |

## DOWNLOAD_USER_AVATAR_MODE

头像下载模式

| 值   | 说明       |
| :--- | :--------- |
| none | 不下载头像 |
| low  | 低清头像   |
| high | 高清头像   |

**低清头像样例**

![1720768108538](./assets/scrape_config/images/1720768108538.jpg)

**高清头像样例**

![1720768116148](./assets/scrape_config/images/1720768116148.jpg)

## SCRAPE_SHARE_ORIGIN `<scrape>`

如果爬取的是转发贴, 是否爬取被转发的原帖

| 值    | 说明   |
| ----- | ------ |
| True  | 爬取   |
| False | 不爬取 |

## UPDATE_SHARE_ORIGIN `<update>`

如果更新的是转发贴, 是否更新被转发的原帖

| 值    | 说明   |
| ----- | ------ |
| True  | 更新   |
| False | 不更新 |
