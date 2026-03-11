from __future__ import annotations

import sqlite3
from pathlib import Path

APP_DIR = Path.home() / ".warningnet"
DB_PATH = APP_DIR / "warningnet.db"


class Database:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS indexed_files (
                    path TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    extension TEXT,
                    size INTEGER,
                    modified_at REAL
                );

                CREATE TABLE IF NOT EXISTS vault_items (
                    id TEXT PRIMARY KEY,
                    original_name TEXT NOT NULL,
                    stored_path TEXT NOT NULL,
                    created_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module TEXT NOT NULL,
                    action TEXT NOT NULL,
                    created_at REAL NOT NULL
                );
                """
            )

    def set_setting(self, key: str, value: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    def get_setting(self, key: str, default: str = "") -> str:
        with self.connect() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else default

    def log_activity(self, module: str, action: str) -> None:
        import time

        with self.connect() as conn:
            conn.execute(
                "INSERT INTO activities(module, action, created_at) VALUES(?, ?, ?)",
                (module, action, time.time()),
            )
