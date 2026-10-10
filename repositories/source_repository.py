import mysql.connector

from config.database import Database
from models.source import Source
from repositories.base_repository import BaseRepository


SOURCE_COLUMNS = """
    id, name, domain, path, category_id, description, status,
    link_selector, title_selector, description_selector,
    content_selector, comment_selector, remove_selector,
    image_selector, author_selector, published_at_selector,
    created_at, updated_at, deleted_at
"""


class SourceRepository(BaseRepository):
    def __init__(self, database=None):
        self.db = database or Database()

    @staticmethod
    def _to_model(row):
        return Source(**row) if row else None

    def _find_many(self, active_only=False):
        where = "deleted_at IS NULL"
        if active_only:
            where += " AND status = 1"
        sql = f"SELECT {SOURCE_COLUMNS} FROM sources WHERE {where} ORDER BY id"
        try:
            with self.db.get_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(sql)
                    return [self._to_model(row) for row in cursor.fetchall()]
        except mysql.connector.Error as error:
            print(f"Lỗi đọc nguồn tin: {error}")
            return []

    def find_all(self):
        return self._find_many()

    def find_active(self):
        return self._find_many(active_only=True)

    def find_by_id(self, source_id):
        sql = f"SELECT {SOURCE_COLUMNS} FROM sources WHERE id = %s AND deleted_at IS NULL"
        try:
            with self.db.get_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(sql, (source_id,))
                    return self._to_model(cursor.fetchone())
        except mysql.connector.Error as error:
            print(f"Lỗi tìm nguồn tin: {error}")
            return None

    def find_by_location(self, domain, path):
        sql = f"""
            SELECT {SOURCE_COLUMNS} FROM sources
            WHERE domain = %s AND COALESCE(path, '') = COALESCE(%s, '')
              AND deleted_at IS NULL LIMIT 1
        """
        try:
            with self.db.get_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(sql, (domain, path))
                    return self._to_model(cursor.fetchone())
        except mysql.connector.Error as error:
            print(f"Lỗi kiểm tra nguồn tin: {error}")
            return None

    @staticmethod
    def _values(source):
        return (
            source.name, source.domain, source.path, source.category_id,
            source.description, 1 if source.status else 0, source.link_selector,
            source.title_selector, source.description_selector,
            source.content_selector, source.comment_selector,
            source.remove_selector, source.image_selector,
            source.author_selector, source.published_at_selector,
        )

    def create(self, source):
        sql = """
            INSERT INTO sources (
                name, domain, path, category_id, description, status,
                link_selector, title_selector, description_selector,
                content_selector, comment_selector, remove_selector,
                image_selector, author_selector, published_at_selector
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            with self.db.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, self._values(source))
                    connection.commit()
                    source.id = cursor.lastrowid
                    return True
        except mysql.connector.Error as error:
            print(f"Lỗi thêm nguồn tin: {error}")
            return False

    def update(self, source):
        sql = """
            UPDATE sources SET
                name = %s, domain = %s, path = %s, category_id = %s,
                description = %s, status = %s, link_selector = %s,
                title_selector = %s, description_selector = %s,
                content_selector = %s, comment_selector = %s,
                remove_selector = %s, image_selector = %s,
                author_selector = %s, published_at_selector = %s
            WHERE id = %s AND deleted_at IS NULL
        """
        try:
            with self.db.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, (*self._values(source), source.id))
                    connection.commit()
                    return cursor.rowcount > 0
        except mysql.connector.Error as error:
            print(f"Lỗi cập nhật nguồn tin: {error}")
            return False

    def change_status(self, source_id, status):
        sql = "UPDATE sources SET status = %s WHERE id = %s AND deleted_at IS NULL"
        try:
            with self.db.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, (1 if status else 0, source_id))
                    connection.commit()
                    return cursor.rowcount > 0
        except mysql.connector.Error as error:
            print(f"Lỗi đổi trạng thái nguồn tin: {error}")
            return False

    def soft_delete(self, source_id):
        sql = """
            UPDATE sources SET deleted_at = CURRENT_TIMESTAMP, status = 0
            WHERE id = %s AND deleted_at IS NULL
        """
        try:
            with self.db.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, (source_id,))
                    connection.commit()
                    return cursor.rowcount > 0
        except mysql.connector.Error as error:
            print(f"Lỗi xóa nguồn tin: {error}")
            return False
