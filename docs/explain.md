### 为什么本程序不把 post_assets、user_avatar 先记录到数据库, 到最后再集中下载

本程序可以把 post_assets、user_avatar 先记录到数据库, 到最后再集中下载。这样 需要过滤掉 `author_and_replied_posts_with_subposts` 、`author_and_replied_posts_with_author_subposts` 就不需要删除数据了

> 答
>
> 因为我无法得知文件的后缀名, 文件类型的识别是依靠的 http 的 content_type 表头。虽然目前的图片、视频、音频的格式是固定的。但是如果以后出现了新的格式, 那么程序就很难修改。
