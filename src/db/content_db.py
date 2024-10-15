import os
import sqlite3
from enum import Enum
from typing import Callable, Tuple, List

from config.scraper_config import SCRAPER_VERSION
from pojo.content_frag import ContentFragType


class DBInfoKey(Enum):
    SCRAPER_VERSION = "scraper_version"
    THREAD_ID = "thread_id"


class ContentDB(sqlite3.Connection):
    thread_id: int = 0

    def __init__(self, file_path: str, thread_id: int):
        self.thread_id = thread_id
        is_exists = os.path.exists(file_path)

        super().__init__(file_path)
        self.isolation_level = None  # 开启自动提交
        self.execute("pragma journal_mode=wal;")

        if is_exists:
            self.transaction(self.__update_db_structure)
        else:
            self.transaction(self.__create_db_structure)

    def __create_db_structure(self) -> None:
        # DDL
        ddl = """
            DROP TABLE IF EXISTS db_info;
            CREATE TABLE db_info
            (
                k TEXT PRIMARY KEY,
                v TEXT NOT NULL
            );

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
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                portrait    TEXT    DEFAULT NULL NULL,
                username    TEXT    DEFAULT NULL NULL,
                nickname    TEXT               NOT NULL,
                tieba_uid   INTEGER DEFAULT NULL NULL,
                avatar      TEXT    DEFAULT NULL NULL,
                glevel      INTEGER DEFAULT 0  NOT NULL,
                gender      INTEGER DEFAULT 0  NOT NULL,
                ip          TEXT    DEFAULT '' NOT NULL,
                is_vip      BOOLEAN DEFAULT 0  NOT NULL,
                is_god      BOOLEAN DEFAULT 0  NOT NULL,
                age         FLOAT              NOT NULL,
                sign        TEXT    DEFAULT '' NOT NULL,
                post_num    INTEGER DEFAULT 0  NOT NULL,
                agree_num   INTEGER DEFAULT 0  NOT NULL,
                fan_num     INTEGER DEFAULT 0  NOT NULL,
                follow_num  INTEGER DEFAULT 0  NOT NULL,
                forum_num   INTEGER DEFAULT 0  NOT NULL,
                level       INTEGER DEFAULT 0  NOT NULL,
                is_bawu     BOOLEAN DEFAULT 0  NOT NULL,
                status      INTEGER DEFAULT 0  NOT NULL,
                completed   BOOLEAN DEFAULT 0  NOT NULL,
                scrape_time INTEGER DEFAULT 0  NOT NULL
            );
            CREATE UNIQUE INDEX 'uk_user(portrait)' ON 'user'(portrait);
            CREATE UNIQUE INDEX 'uk_user(tieba_uid)' ON 'user'(tieba_uid);
            CREATE INDEX 'idx_user(completed)' ON 'user'(completed);

            DROP TABLE IF EXISTS user_info_history;
            CREATE TABLE user_info_history
            (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                portrait    TEXT    DEFAULT NULL NULL,
                username    TEXT    DEFAULT NULL NULL,
                tieba_uid   INTEGER DEFAULT NULL NULL,
                field_name  TEXT              NOT NULL,
                field_value TEXT              NOT NULL,
                scrape_time INTEGER DEFAULT 0 NOT NULL
            );
            CREATE INDEX 'idx_user(tieba_uid)' ON user_info_history (tieba_uid);
            CREATE INDEX 'idx_user_info_history(portrait)' ON user_info_history (portrait);
            CREATE INDEX 'idx_user_info_history(field_name)' ON user_info_history (field_name);

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
        self.executescript(ddl)

        self.__insert_db_info_data()

        # content_fragment_type
        content_fragment_type_insert_sql = "INSERT INTO content_fragment_type(id, type) VALUES (?, ?); "
        content_fragment_type_insert_params = [
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
        self.executemany(content_fragment_type_insert_sql, content_fragment_type_insert_params)

    def __update_db_structure(self):
        # 模拟 switch 语句
        def update_process():
            # 读取 db_info
            scraper_version: str | None = None

            sql_db_info_select_sql = "SELECT * FROM sqlite_master WHERE type='table' AND name='db_info';"
            sql_scraper_version_select = (
                f"SELECT v FROM db_info WHERE k = '{DBInfoKey.SCRAPER_VERSION.value}';"
            )
            sql_scraper_version_update = (
                f"UPDATE db_info SET v = '{SCRAPER_VERSION}' WHERE k = '{DBInfoKey.SCRAPER_VERSION.value}';"
            )
            if self.execute(sql_db_info_select_sql).fetchone():
                row = self.execute(sql_scraper_version_select).fetchone()
                if row is not None:
                    scraper_version = row[0]

            if scraper_version is None:
                sql_alter__v_1_3_0 = """
                    DROP TABLE IF EXISTS db_info;
                    CREATE TABLE db_info
                    (
                        k TEXT PRIMARY KEY,
                        v TEXT NOT NULL
                    );

                    ALTER TABLE user ADD COLUMN completed BOOLEAN DEFAULT 0 NOT NULL;
                    CREATE INDEX 'idx_user(completed)' ON 'user'(completed);
                    UPDATE user SET completed = 1;
                    ALTER TABLE user ADD COLUMN scrape_time INTEGER DEFAULT 0 NOT NULL;

                    DROP TABLE IF EXISTS user_info_history;
                    CREATE TABLE user_info_history
                    (
                        id          INTEGER PRIMARY KEY AUTOINCREMENT,
                        portrait    TEXT    DEFAULT NULL NULL,
                        username    TEXT    DEFAULT NULL NULL,
                        tieba_uid   INTEGER DEFAULT NULL NULL,
                        field_name  TEXT              NOT NULL,
                        field_value TEXT              NOT NULL,
                        scrape_time INTEGER DEFAULT 0 NOT NULL
                    );
                    CREATE INDEX 'idx_user(tieba_uid)' ON user_info_history (tieba_uid);
                    CREATE INDEX 'idx_user_info_history(portrait)' ON user_info_history (portrait);
                    CREATE INDEX 'idx_user_info_history(field_name)' ON user_info_history (field_name);
                """
                self.executescript(sql_alter__v_1_3_0)
                self.__insert_db_info_data()
                yield "执行数据库升级 v1.2.1 -> v1.3.0 "
            if "1.3.0" == scraper_version:
                # sql_alter__v_1_3_1 = """"""
                # self.executescript(sql_alter__v_1_3_1)
                yield "执行数据库升级 v1.3.0 -> v1.3.1 "
            if "1.3.1" == scraper_version:
                yield "最新版本，无需更新"

            self.execute(sql_scraper_version_update)
            yield "更新 scraper_version 完成"

        for msg in update_process():
            pass

    def __insert_db_info_data(self):
        db_info_insert_sql = "INSERT INTO db_info VALUES (?, ?);"
        db_info_insert_params: List[Tuple[str, str]] = [
            (DBInfoKey.SCRAPER_VERSION.value, SCRAPER_VERSION),
            (DBInfoKey.THREAD_ID.value, str(self.thread_id)),
        ]
        self.executemany(db_info_insert_sql, db_info_insert_params)

    def transaction(self, func: Callable[[], None]) -> None:
        """
        事务处理

        Args:
            func: 事务内要执行的函数

        """
        try:
            self.execute("BEGIN")
            func()
            self.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.rollback()
            raise e
