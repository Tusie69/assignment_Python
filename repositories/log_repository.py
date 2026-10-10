import mysql.connector

from config.database import Database
from models.crawl_log import CrawlLog


class LogRepository:
    def __init__(self, database=None):
        self.db = database or Database()

    def create(self, log):
        sql = """
            INSERT INTO logs (
                source_id, action, status, message, total_articles,
                new_articles, updated_articles, skipped_articles,
                started_at, finished_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            log.source_id, log.action, log.status, log.message,
            log.total_articles, log.new_articles, log.updated_articles,
            log.skipped_articles, log.started_at, log.finished_at,
        )
        try:
            with self.db.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, params)
                    connection.commit()
                    log.id = cursor.lastrowid
                    return True
        except mysql.connector.Error as error:
            print(f"Lỗi thêm nhật ký crawl: {error}")
            return False

    def update(self, log):
        sql = """
            UPDATE logs SET status = %s, message = %s, total_articles = %s,
                new_articles = %s, updated_articles = %s,
                skipped_articles = %s, finished_at = %s
            WHERE id = %s
        """
        params = (
            log.status, log.message, log.total_articles, log.new_articles,
            log.updated_articles, log.skipped_articles, log.finished_at, log.id,
        )
        try:
            with self.db.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, params)
                    connection.commit()
                    return cursor.rowcount > 0
        except mysql.connector.Error as error:
            print(f"Lỗi cập nhật nhật ký crawl: {error}")
            return False

    def find_recent(self, limit=20):
        sql = "SELECT * FROM logs ORDER BY id DESC LIMIT %s"
        try:
            with self.db.get_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(sql, (max(1, int(limit)),))
                    return [CrawlLog(**row) for row in cursor.fetchall()]
        except mysql.connector.Error as error:
            print(f"Lỗi đọc nhật ký crawl: {error}")
            return []
