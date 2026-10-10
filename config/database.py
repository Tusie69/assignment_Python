import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


class Database:
    """Tạo kết nối MySQL mới cho từng thao tác repository."""

    def __init__(self, **overrides):
        self.config = {
            "host": overrides.get("host", os.getenv("DB_HOST", "localhost")),
            "port": int(overrides.get("port", os.getenv("DB_PORT", "3306"))),
            "user": overrides.get("user", os.getenv("DB_USER", "root")),
            "password": overrides.get("password", os.getenv("DB_PASSWORD", "")),
            "database": overrides.get("database", os.getenv("DB_NAME", "crawler_me")),
            "charset": "utf8mb4",
            "use_unicode": True,
            "connection_timeout": 10,
        }

    def get_connection(self):
        """Trả về connection; caller dùng ``with`` để tự động đóng."""
        return mysql.connector.connect(**self.config)

    def test_connection(self):
        try:
            with self.get_connection() as connection:
                return connection.is_connected()
        except mysql.connector.Error:
            return False
