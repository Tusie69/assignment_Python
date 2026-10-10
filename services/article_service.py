import csv
import json
from datetime import date, datetime
from pathlib import Path

from models.article import Article
from repositories.article_repository import ArticleRepository


class ArticleService:
    def __init__(self, repository=None):
        self.repository = repository or ArticleRepository()

    @staticmethod
    def _pagination(page, page_size):
        try:
            page = int(page)
            page_size = int(page_size)
        except (TypeError, ValueError) as error:
            raise ValueError("Trang và số lượng bài phải là số nguyên") from error
        if page < 1 or page_size < 1:
            raise ValueError("Trang và số lượng bài phải lớn hơn 0")
        return page, page_size

    @staticmethod
    def _date(value):
        if not value:
            return None
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date()
        except ValueError as error:
            raise ValueError("Ngày phải đúng định dạng YYYY-MM-DD") from error

    def find_all(self, page=1, page_size=10):
        page, page_size = self._pagination(page, page_size)
        return self.repository.find_all(page, page_size)

    def count_all(self):
        return self.repository.count_all()

    def find_by_id(self, article_id):
        if article_id is None:
            return None
        return self.repository.find_by_id(article_id)

    def search(self, keyword, page=1, page_size=10):
        if not keyword or not keyword.strip():
            raise ValueError("Từ khóa không được để trống")
        page, page_size = self._pagination(page, page_size)
        return self.repository.search(keyword.strip(), page, page_size)

    def count_search(self, keyword):
        if not keyword or not keyword.strip():
            return 0
        return self.repository.count_search(keyword.strip())

    def filter(self, source_id=None, crawled_date=None, page=1, page_size=10):
        page, page_size = self._pagination(page, page_size)
        parsed_date = self._date(crawled_date)
        return self.repository.filter(source_id, parsed_date, page, page_size)

    def count_filter(self, source_id=None, crawled_date=None):
        return self.repository.count_filter(source_id, self._date(crawled_date))

    def filter_by_source(self, source_id, page=1, page_size=10):
        return self.filter(source_id=source_id, page=page, page_size=page_size)

    def filter_by_crawled_date(self, value, page=1, page_size=10):
        return self.filter(crawled_date=value, page=page, page_size=page_size)

    def filter_by_source_and_date(self, source_id, value, page=1, page_size=10):
        return self.filter(source_id, value, page, page_size)

    def soft_delete(self, article_id):
        if article_id is None:
            return False
        return self.repository.soft_delete(article_id)

    @staticmethod
    def _export_row(article):
        values = vars(article).copy()
        for key, value in values.items():
            if isinstance(value, (datetime, date)):
                values[key] = value.isoformat(sep=" ") if isinstance(value, datetime) else value.isoformat()
        return values

    def export(self, file_format="csv", output_directory="exports"):
        file_format = file_format.lower()
        if file_format not in ("csv", "json"):
            raise ValueError("Chỉ hỗ trợ định dạng CSV hoặc JSON")

        articles = []
        page = 1
        while True:
            batch = self.find_all(page, 100)
            if not batch:
                break
            articles.extend(batch)
            page += 1

        output_path = Path(output_directory)
        output_path.mkdir(parents=True, exist_ok=True)
        file_path = output_path / f"articles_{datetime.now():%Y%m%d_%H%M%S}.{file_format}"
        rows = [self._export_row(article) for article in articles]

        if file_format == "json":
            with file_path.open("w", encoding="utf-8") as file:
                json.dump(rows, file, ensure_ascii=False, indent=2)
        else:
            fieldnames = list(rows[0].keys()) if rows else list(vars(Article()).keys())
            with file_path.open("w", encoding="utf-8-sig", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        return file_path, len(rows)
