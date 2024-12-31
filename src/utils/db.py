from contextlib import contextmanager
import sqlite3
import os


class Database:
    DATABASE_URL = f'{os.getcwd()}/aigc_video.db'

    def __init__(self):
        self.conn = sqlite3.connect(self.DATABASE_URL)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        self.conn.commit()
        self.conn.close()


@contextmanager
def get_db():
    db = Database()
    try:
        yield db.conn.cursor()
    finally:
        db.close()



def init_tables():
    with get_db() as db:
        db.execute('CREATE TABLE IF NOT EXISTS video(id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(255), content TEXT, sentences TEXT, dst VARCHAR(255), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        db.execute('CREATE TABLE IF NOT EXISTS setting(id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(255) NOT NULL UNIQUE, value TEXT, descr TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        db.execute('''INSERT OR IGNORE INTO setting(name, descr, `value`)
                      VALUES ('volcengine.tts.appkey', '火山引擎语音应用的appkey', ''),
                             ('volcengine.tts.service', '火山引擎语音应用的service', 'sami'),
                             ('volcengine.tts.region', '火山引擎语音应用的区域', 'cn-north-1'),
                             ('volcengine.tts.token_version', '火山引擎语音应用的token version', 'volc-auth-v1'),
                             ('volcengine.access_key', '火山引擎语音access_key', ''),
                             ('volcengine.access_secret', '火山引擎语音access_secret', '')
                   ''')
