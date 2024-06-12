DROP TABLE IF EXISTS post;
CREATE TABLE post
(
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    contents         TEXT               NOT NULL, -- json [{ type: 1, }]
    floor            INTEGER            NOT NULL, -- 楼和楼中楼一样
    user_id          INTEGER            NOT NULL,
    agree            INTEGER DEFAULT 0  NOT NULL,
    disagree         INTEGER DEFAULT 0  NOT NULL,
    create_time      INTEGER            NOT NULL, -- 创建时间，要依赖爬取的时间
    is_thread_author BOOLEAN DEFAULT 0  NOT NULL, -- 冗余字段， 区分楼主和普通用户
    sign             TEXT    DEFAULT '' NOT NULL, -- 小尾巴，post独有,
    reply_num        INTEGER DEFAULT 0  NOT NULL, -- 楼独有，冗余字段，不需要join。
    parent_id        INTEGER DEFAULT 0  NOT NULL, -- 楼中楼独有, 区分普通楼和楼中的唯一标识 where parent_id == 0
    reply_to_id      INTEGER DEFAULT 0  NOT NULL  -- 楼中楼独有，不是所有的楼中楼都有reply_to_id。要回复的user_id.不是Post_id。b站是保存的Post_id
);
CREATE INDEX 'idx_post(floor)' ON post(floor);
CREATE INDEX 'idx_post(user_id)' ON post(user_id);
CREATE INDEX 'idx_post(agree)' ON post(agree); -- 根据点赞数排序
CREATE INDEX 'idx_post(create_time)' ON post(create_time); -- 根据创建时间排序
CREATE INDEX 'idx_post(is_thread_author)' ON post(is_thread_author); -- 根据楼主和普通用户区分
CREATE INDEX 'idx_post(parent_id)' ON post(parent_id);



DROP TABLE IF EXISTS 'user';
CREATE TABLE user
(
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    portrait   TEXT               NOT NULL, -- portrait可以作为唯一的key，
    username   TEXT    DEFAULT NULL NULL,
    nickname   TEXT               NOT NULL, -- nick_name_new > nick_name > show_name > log_name
    avatar     TEXT    DEFAULT '' NOT NULL,
    glevel     INTEGER DEFAULT 0  NOT NULL, -- 成长等级
    gender     INTEGER DEFAULT 0  NOT NULL, -- 0 unknown, 1 male, 2 female
    ip         TEXT    DEFAULT '' NOT NULL,
    is_vip     BOOLEAN DEFAULT 0  NOT NULL, -- 是贵族
    is_god     BOOLEAN DEFAULT 0  NOT NULL, -- 是大神
    tieba_uid  INTEGER DEFAULT NULL NULL,-- get_userinfo()
    age        FLOAT              NOT NULL,-- get_userinfo()
    sign       TEXT    DEFAULT '' NOT NULL,-- get_userinfo() 小尾巴
    post_num   INTEGER DEFAULT 0  NOT NULL, -- get_userinfo()
    agree_num  INTEGER DEFAULT 0  NOT NULL,-- get_userinfo()
    fan_num    INTEGER DEFAULT 0  NOT NULL,-- get_userinfo() 粉丝数
    follow_num INTEGER DEFAULT 0  NOT NULL, -- get_userinfo() 关注数量
    forum_num  INTEGER DEFAULT 0  NOT NULL,-- get_userinfo() 贴吧数量
    -- 吧相关
    level      INTEGER DEFAULT 0  NOT NULL, -- 在这个吧的等级
    is_bawu    BOOLEAN DEFAULT 0  NOT NULL,  -- 是吧务 link
    status     INTEGER DEFAULT 0  NOT NULL -- 0 正常，1 注销
);
CREATE UNIQUE INDEX 'uk_user(portrait)' ON 'user'(portrait);
CREATE UNIQUE INDEX 'uk_user(username)' ON 'user'(username);
CREATE UNIQUE INDEX 'uk_user(tieba_uid)' ON 'user'(tieba_uid);



DROP TABLE IF EXISTS content_fragment_type;
CREATE TABLE content_fragment_type
(
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL
);



DROP TABLE IF EXISTS tieba_origin_src;
CREATE TABLE tieba_origin_src
(
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    filename          TEXT    NOT NULL,
    content_frag_type INTEGER NOT NULL,
    origin_src        TEXT    NOT NULL
);
CREATE UNIQUE INDEX 'uk_tieba_origin_src(filename)' ON tieba_origin_src(filename);
CREATE INDEX 'idx_tieba_origin_src(content_frag_type)' ON tieba_origin_src(content_frag_type);
