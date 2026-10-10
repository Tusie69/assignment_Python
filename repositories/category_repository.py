import mysql.connector

from config.database import Database
from models.category import Category
from repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository):
    def __init__(self, database=None):
        self.db = database or Database()

    @staticmethod
    def _to_model(row):
        return Category(**row) if row else None

    def find_all(self):
        sql = "SELECT * FROM categories WHERE deleted_at IS NULL ORDER BY id"
        try:
            with self.db.get_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(sql)
                    return [self._to_model(row) for row in cursor.fetchall()]
        except mysql.connector.Error as error:
            print(f"Lỗi đọc danh mục: {error}")
            return []

    def find_by_id(self, category_id):
        sql = "SELECT * FROM categories WHERE id = %s AND deleted_at IS NULL"
        try:
            with self.db.get_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(sql, (category_id,))
                    return self._to_model(cursor.fetchone())
        except mysql.connector.Error as error:
            print(f"Lỗi tìm danh mục: {error}")
            return None

    def create(self, category):
        sql = "INSERT INTO categories (name, description, alias, slug) VALUES (%s, %s, %s, %s)"
        try:
            with self.db.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, (category.name, category.description, category.alias, category.slug))
                    connection.commit()
                    category.id = cursor.lastrowid
                    return True
        except mysql.connector.Error as error:
            print(f"Lỗi thêm danh mục: {error}")
            return False

    def update(self, category):
        sql = """
            UPDATE categories SET name = %s, description = %s, alias = %s, slug = %s
            WHERE id = %s AND deleted_at IS NULL
        """
        try:
            with self.db.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, (category.name, category.description, category.alias, category.slug, category.id))
                    connection.commit()
                    return cursor.rowcount > 0
        except mysql.connector.Error as error:
            print(f"Lỗi cập nhật danh mục: {error}")
            return False

    def soft_delete(self, category_id):
        sql = "UPDATE categories SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s AND deleted_at IS NULL"
        try:
            with self.db.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, (category_id,))
                    connection.commit()
                    return cursor.rowcount > 0
        except mysql.connector.Error as error:
            print(f"Lỗi xóa danh mục: {error}")
            return False
