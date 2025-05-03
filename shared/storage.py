# shared/storage.py
import sqlite3
from shared.config import Config
from shared.logger import get_logger

logger = get_logger(__name__)

class Storage:
    def __init__(self, db_path: str = Config.STORAGE_DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self._ensure_tables()

    def _ensure_tables(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            raw TEXT,
            processed TEXT,
            response TEXT
        );
        CREATE TABLE IF NOT EXISTS state (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        '''
        self.conn.executescript(sql)
        self.conn.commit()
        logger.debug("Database tables ensured.")

    def save_log(self, timestamp: str, raw: str, processed: str, response: str):
        self.conn.execute(
            "INSERT INTO logs (timestamp, raw, processed, response) VALUES (?, ?, ?, ?)",
            (timestamp, raw, processed, response)
        )
        self.conn.commit()
        logger.debug("Log saved to database.")

    def get_state(self, key: str) -> str:
        cur = self.conn.execute(
            "SELECT value FROM state WHERE key = ?", (key,)
        )
        row = cur.fetchone()
        return row[0] if row else None

    def set_state(self, key: str, value: str):
        self.conn.execute(
            "REPLACE INTO state (key, value) VALUES (?, ?)", (key, value)
        )
        self.conn.commit()
        logger.debug(f"State updated: {key} = {value}")