# Note

## Thead

### share_origin

```json
{
    "share_origin": {
        "contents": {
            "objs": [],
            "texts": [],
            "emojis": [],
            "imgs": [],
            "ats": [],
            "links": [],
            "tiebapluses": [],
            "video": {
                "src": "",
                "cover_src": "",
                "duration": 0,
                "width": 0,
                "height": 0,
                "view_num": 0
            },
            "voice": {
                "md5": "",
                "duration": 0
            }
        },
        "title": "",
        "fid": 0,
        "fname": "",
        "tid": 0,
        "author_id": 0,
        "vote_info": {
            "title": "",
            "is_multi": false,
            "options": [],
            "total_vote": 0,
            "total_user": 0
        }
    }
}
```

### 投票

```json
{
    "vote_info": {
        "title": "t",
        "is_multi": false,
        "options": [
            {
                "vote_num": 1488,
                "text": "t1"
            },
            {
                "vote_num": 304,
                "text": "t2"
            }
        ],
        "total_vote": 1792,
        "total_user": 1792
    }
}
```

## Post

### 文件唯一标识

目前来看贴吧应该用是 md5

### text

文本内容

text 属性可能是历史遗留问题。

### IP 属地

贴吧不是每个帖子都保存发布时的 ip 地址。会随着用户的 ip 改变

有些没有一直没登陆的用户爬不出 ip。

### 被回复者

贴吧表达被回复者有三种方式

-   写入 contents 不做任何处理，直接把被回复者的用户名嵌入到文本中。（早期帖子）

这种可以在爬取的时候完善数据，但是很容易误判。本程序会尽可能的把用户给爬取下来。但是不会去修改原本的数据。

```powershell
回复 $username ：
```

-   写入 contents+FragAT（早期帖子）

爬取时可以可以根据 user_name 向已经爬取的用户中查找 user_id 并补全 FragAT 里的 user_id，因为贴吧的 username 不可改。

```powershell
Contents(
    objs=[
        FragText(
            text='回复 '
        ),
        FragAT(
            text='$user_name',
            user_id=0
        )
        FragText(
            text=' :'
        ),
    ]
)
```

-   reply_to_id（目前官方的使用的方法)

用 reply_to_id 属性表明了回复者。

### reply_num

只会增加。不会减少。

删除楼中楼，不会减少 reply_num 的值。

### 话题

话题是纯文本。用##包裹，

用百度的 api 去搜索。

### 视频

每条贴子只能发一条视频。

```json
{
    "video": {
        "src": "",
        "cover_src": "",
        "duration": 0,
        "width": 0,
        "height": 0,
        "view_num": 0
    }
}
```

### 语音

每条帖子只能发一条语音。

```json
{
    "voice": {
        "md5": "",
        "duration": 0
    }
}
```

语音下载地址

```powershell
https://tiebac.baidu.com/c/p/voice?voice_md5=$voice_md5&play_from=pb_voice_play
```

### tiebapluse

我不知道这是什么东西，没见过。

### 小尾巴 sign

已经发布的小尾巴不会随着用户修改小尾巴而改变。

### Create_Time

是中国标准时区，不是 gmt

### 分块编号

```python
_type = proto.type
# 0纯文本 9电话号 18话题 27百科词条 40梗百科
if _type in [0, 9, 18, 27, 40]:
    frag = FragText_p.from_tbdata(proto)
    texts.append(frag)
    yield frag
# 11:tid=5047676428
elif _type in [2, 11]:
    frag = FragEmoji_p.from_tbdata(proto)
    emojis.append(frag)
    yield frag
# 20:tid=5470214675
elif _type in [3, 20]:
    frag = FragImage_p.from_tbdata(proto)
    imgs.append(frag)
    yield frag
elif _type == 4:
    frag = FragAt_p.from_tbdata(proto)
    ats.append(frag)
    texts.append(frag)
    yield frag
elif _type == 1:
    frag = FragLink_p.from_tbdata(proto)
    links.append(frag)
    texts.append(frag)
    yield frag
elif _type == 10:  # voice
    frag = FragVoice_p.from_tbdata(proto)
    nonlocal voice
    voice = frag
    yield frag
elif _type == 5:  # video
    frag = FragVideo_p.from_tbdata(proto)
    nonlocal video
    video = frag
    yield frag
# 35|36:tid=7769728331 / 37:tid=7760184147
elif _type in [35, 36, 37]:
    frag = FragTiebaPlus_p.from_tbdata(proto)
    tiebapluses.append(frag)
    texts.append(frag)
    yield frag
# outdated tiebaplus
elif _type == 34:
    continue
```

### 设备 （无）

网页端会显示设备，但是移动端 api 没有设备信息。

![1717232574390](./assets/note/images/1717232574390.png)

## Comments

结构基本和 post 相似

## User

### 用户唯一标识

-   username

可能为空，早期互联网需要填写用户名。但是现在很多账号没有用户名

-   user_id

一定不为空

-   portrait

一定不为空, 很重要的参数。

-   tieba_uid

可能为空， 也没什么用

### 头像

目前百度贴吧移动端用 `portrait` 这一参数来请求头像图片。

```powershell
# 小头像
 # t=$timestamp 这个参数我猜测是头像修改的时间
https://gss0.baidu.com/7Ls0a8Sm2Q5IlBGlnYG/sys/portrait/item/$portrait?t=$timestamp
http://tb.himg.baidu.com/sys/portrait/item/$portrait

# 高清头像
https://himg.bdimg.com/sys/portraith/item/$portrait
```

> 要注意的是，你在网页端浏览帖子时看到的用户头像可能会与爬取到的图片不一样。因为爬取头像依靠的是 `https://himg.bdimg.com/sys/portraith/item/$portrait` 这个接口。网页端由于其特殊的加载方式导致有些有年代的帖子会加载过时的头像（用户以前的头像）。

### level 和 glevel

level 吧内等级

glevel 贴吧成长等级
