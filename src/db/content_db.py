import sqlite3
from typing import Callable

from pojo.content_frag import ContentFragType


class ContentDB(sqlite3.Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.isolation_level = None  # 开启自动提交
        self.execute("pragma journal_mode=wal;")
        self.__data_definition()  # 创建表
        self.__insert_content_fragment_type()  # 插入一些提前定义的数据

    def __data_definition(self) -> None:
        DDL = """
        DROP TABLE IF EXISTS post;
        CREATE TABLE post
        (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            contents         TEXT               NOT NULL,
            floor            INTEGER            NOT NULL,
            user_id          INTEGER            NOT NULL,
            agree            INTEGER DEFAULT 0  NOT NULL,
            disagree         INTEGER DEFAULT 0  NOT NULL,
            create_time      INTEGER            NOT NULL,
            is_thread_author BOOLEAN DEFAULT 0  NOT NULL,
            sign             TEXT    DEFAULT '' NOT NULL,
            reply_num        INTEGER DEFAULT 0  NOT NULL,
            parent_id        INTEGER DEFAULT 0  NOT NULL,
            reply_to_id      INTEGER DEFAULT 0  NOT NULL
        );
        CREATE INDEX 'idx_post(floor)' ON post (floor);
        CREATE INDEX 'idx_post(user_id)' ON post (user_id);
        CREATE INDEX 'idx_post(agree)' ON post (agree);
        CREATE INDEX 'idx_post(create_time)' ON post (create_time);
        CREATE INDEX 'idx_post(is_thread_author)' ON post (is_thread_author);
        CREATE INDEX 'idx_post(parent_id)' ON post (parent_id);


        DROP TABLE IF EXISTS 'user';
        CREATE TABLE user
        (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            portrait   TEXT    DEFAULT NULL NULL,
            username   TEXT    DEFAULT NULL NULL,
            nickname   TEXT                 NOT NULL,
            tieba_uid  INTEGER DEFAULT NULL NULL,
            avatar     TEXT    DEFAULT NULL NULL,
            glevel     INTEGER DEFAULT 0    NOT NULL,
            gender     INTEGER DEFAULT 0    NOT NULL,
            ip         TEXT    DEFAULT ''   NOT NULL,
            is_vip     BOOLEAN DEFAULT 0    NOT NULL,
            is_god     BOOLEAN DEFAULT 0    NOT NULL,
            age        FLOAT                NOT NULL,
            sign       TEXT    DEFAULT ''   NOT NULL,
            post_num   INTEGER DEFAULT 0    NOT NULL,
            agree_num  INTEGER DEFAULT 0    NOT NULL,
            fan_num    INTEGER DEFAULT 0    NOT NULL,
            follow_num INTEGER DEFAULT 0    NOT NULL,
            forum_num  INTEGER DEFAULT 0    NOT NULL,
            level      INTEGER DEFAULT 0    NOT NULL,
            is_bawu    BOOLEAN DEFAULT 0    NOT NULL,
            status     INTEGER DEFAULT 0    NOT NULL
        );
        CREATE UNIQUE INDEX 'uk_user(portrait)' ON 'user' (portrait);
        CREATE UNIQUE INDEX 'uk_user(tieba_uid)' ON 'user' (tieba_uid);


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
        CREATE UNIQUE INDEX 'uk_tieba_origin_src(filename)' ON tieba_origin_src (filename);
        CREATE INDEX 'idx_tieba_origin_src(content_frag_type)' ON tieba_origin_src (content_frag_type);
        """
        self.executescript(DDL)

    def __insert_content_fragment_type(self) -> None:
        params = [
            (ContentFragType.TEXT, "text"),
            (ContentFragType.EMOJI, "emoji"),
            (ContentFragType.IMAGE, "image"),
            (ContentFragType.AT, "at"),
            (ContentFragType.LINK, "link"),
            (ContentFragType.TIEBAPLUS, "tiebaplus"),
            (ContentFragType.VIDEO, "video"),
            (ContentFragType.VOICE, "voice"),
            (ContentFragType.SCRAPE_ERROR, "scrape_error"),
        ]
        sql = "INSERT INTO content_fragment_type(id, type) VALUES (?, ?); "
        self.executemany(sql, params)

    def transaction(self, func: Callable[[], None]) -> bool:
        """
        事务处理

        Args:
            func: 事务内要执行的函数

        Returns:
            bool: 事务是否成功提交，True表示成功，False表示失败

        """
        try:
            self.execute("BEGIN")
            func()
            self.commit()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            self.rollback()
            return False
