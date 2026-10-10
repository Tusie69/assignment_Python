import mysql.connector

from config.database import Database
from models.article import Article
from repositories.base_repository import BaseRepository


ARTICLE_COLUMNS = """
    id, source_id, category_id, title, slug, url, description,
    content, image_url, author, published_at, crawled_at,
    is_rewrite, status, created_at, updated_at, deleted_at
"""


class ArticleRepository(BaseRepository):
    def __init__(self, database=None):
        self.db = database or Database()

    @staticmethod
    def _to_model(row):
        return Article(**row) if row else None

    def _select_many(self, where="deleted_at IS NULL", params=(), page=1, page_size=10):
        page = max(1, int(page))
        page_size = max(1, int(page_size))
        offset = (page - 1) * page_size
        sql = f"""
            SELECT {ARTICLE_COLUMNS}
            FROM articles
            WHERE {where}
            ORDER BY COALESCE(published_at, crawled_at) DESC, id DESC
            LIMIT %s OFFSET %s
        """
        try:
            with self.db.get_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(sql, (*params, page_size, offset))
                    return [self._to_model(row) for row in cursor.fetchall()]
        except mysql.connector.Error as error:
            print(f"Lỗi đọc danh sách bài viết: {error}")
            return []

    def _count(self, where="deleted_at IS NULL", params=()):
        sql = f"SELECT COUNT(*) AS total FROM articles WHERE {where}"
        try:
            with self.db.get_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(sql, params)
                    row = cursor.fetchone()
                    return row["total"] if row else 0
        except mysql.connector.Error as error:
            print(f"Lỗi đếm bài viết: {error}")
            return 0

    def find_all(self, page=1, page_size=10):
        return self._select_many(page=page, page_size=page_size)

    def count_all(self):
        return self._count()

    def find_by_id(self, article_id):
        sql = f"SELECT {ARTICLE_COLUMNS} FROM articles WHERE id = %s AND deleted_at IS NULL"
        try:
            with self.db.get_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(sql, (article_id,))
                    return self._to_model(cursor.fetchone())
        except mysql.connector.Error as error:
            print(f"Lỗi tìm bài viết: {error}")
            return None

    def find_by_url(self, url, include_deleted=True):
        deleted_filter = "" if include_deleted else " AND deleted_at IS NULL"
        sql = f"SELECT {ARTICLE_COLUMNS} FROM articles WHERE url = %s{deleted_filter} LIMIT 1"
        try:
            with self.db.get_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(sql, (url,))
                    return self._to_model(cursor.fetchone())
        except mysql.connector.Error as error:
            print(f"Lỗi kiểm tra URL bài viết: {error}")
            return None

    def create(self, article):
        sql = """
            INSERT INTO articles (
                source_id, category_id, title, slug, url, description,
                content, image_url, author, published_at, crawled_at,
                is_rewrite, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            article.source_id, article.category_id, article.title, article.slug,
            article.url, article.description, article.content, article.image_url,
            article.author, article.published_at, article.crawled_at,
            1 if article.is_rewrite else 0, 1 if article.status else 0,
        )
        try:
            with self.db.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, params)
                    connection.commit()
                    article.id = cursor.lastrowid
                    return True
        except mysql.connector.Error as error:
            print(f"Lỗi thêm bài viết: {error}")
            return False

    def update(self, article):
        sql = """
            UPDATE articles SET
                source_id = %s, category_id = %s, title = %s, slug = %s,
                url = %s, description = %s, content = %s, image_url = %s,
                author = %s, published_at = %s, crawled_at = %s,
                is_rewrite = %s, status = %s, deleted_at = NULL
            WHERE id = %s
        """
        params = (
            article.source_id, article.category_id, article.title, article.slug,
            article.url, article.description, article.content, article.image_url,
            article.author, article.published_at, article.crawled_at,
            1 if article.is_rewrite else 0, 1 if article.status else 0,
            article.id,
        )
        try:
            with self.db.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, params)
                    connection.commit()
                    return cursor.rowcount > 0
        except mysql.connector.Error as error:
            print(f"Lỗi cập nhật bài viết: {error}")
            return False

    def upsert(self, article):
        existing = self.find_by_url(article.url)
        if existing:
            article.id = existing.id
            return self.update(article), "updated"
        return self.create(article), "created"

    @staticmethod
    def _search_condition():
        return "(title LIKE %s OR description LIKE %s OR content LIKE %s) AND deleted_at IS NULL"

    def search(self, keyword, page=1, page_size=10):
        pattern = f"%{keyword}%"
        return self._select_many(
            self._search_condition(), (pattern, pattern, pattern), page, page_size
        )

    def count_search(self, keyword):
        pattern = f"%{keyword}%"
        return self._count(self._search_condition(), (pattern, pattern, pattern))

    def find_by_keyword(self, keyword, page=1, page_size=10):
        return self.search(keyword, page, page_size)

    def filter(self, source_id=None, crawled_date=None, page=1, page_size=10):
        conditions = ["deleted_at IS NULL"]
        params = []
        if source_id is not None:
            conditions.append("source_id = %s")
            params.append(source_id)
        if crawled_date:
            conditions.append("DATE(crawled_at) = %s")
            params.append(crawled_date)
        return self._select_many(" AND ".join(conditions), tuple(params), page, page_size)

    def count_filter(self, source_id=None, crawled_date=None):
        conditions = ["deleted_at IS NULL"]
        params = []
        if source_id is not None:
            conditions.append("source_id = %s")
            params.append(source_id)
        if crawled_date:
            conditions.append("DATE(crawled_at) = %s")
            params.append(crawled_date)
        return self._count(" AND ".join(conditions), tuple(params))

    def filter_by_source(self, source_id, page=1, page_size=10):
        return self.filter(source_id=source_id, page=page, page_size=page_size)

    def filter_by_crawled_date(self, date, page=1, page_size=10):
        return self.filter(crawled_date=date, page=page, page_size=page_size)

    def filter_by_source_and_date(self, source_id, date, page=1, page_size=10):
        return self.filter(source_id, date, page, page_size)

    def soft_delete(self, article_id):
        sql = """
            UPDATE articles
            SET deleted_at = CURRENT_TIMESTAMP, status = 0
            WHERE id = %s AND deleted_at IS NULL
        """
        try:
            with self.db.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, (article_id,))
                    connection.commit()
                    return cursor.rowcount > 0
        except mysql.connector.Error as error:
            print(f"Lỗi xóa bài viết: {error}")
            return False
