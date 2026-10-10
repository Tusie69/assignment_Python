from urllib.parse import urlparse

import soupsieve

from models.source import Source
from repositories.category_repository import CategoryRepository
from repositories.source_repository import SourceRepository


class SourceService:
    def __init__(self, repository=None, category_repository=None):
        self.repository = repository or SourceRepository()
        self.category_repository = category_repository or CategoryRepository()

    def find_all(self):
        return self.repository.find_all()

    def find_active(self):
        return self.repository.find_active()

    def find_by_id(self, source_id):
        return self.repository.find_by_id(source_id)

    @staticmethod
    def _prepare(source):
        source.name = source.name.strip() if source.name else source.name
        source.domain = source.domain.strip().rstrip("/") if source.domain else source.domain
        source.path = (source.path or "").strip()
        if source.path and not source.path.startswith("/"):
            source.path = "/" + source.path

    @staticmethod
    def _validate_selectors(source):
        selector_names = (
            "link_selector", "title_selector", "description_selector",
            "content_selector", "remove_selector", "image_selector",
            "author_selector", "published_at_selector",
        )
        for name in selector_names:
            selector = getattr(source, name, None)
            if selector:
                try:
                    soupsieve.compile(selector)
                except Exception as error:
                    raise ValueError(f"CSS selector '{name}' không hợp lệ: {selector}") from error

    def _validate(self, source):
        if not isinstance(source, Source):
            raise ValueError("Source không hợp lệ")
        self._prepare(source)
        if not source.name:
            raise ValueError("Tên source không được để trống")
        parsed = urlparse(source.domain or "")
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("Domain phải là URL hợp lệ, ví dụ https://example.com")
        if source.category_id is None:
            raise ValueError("Category là bắt buộc")
        if self.category_repository.find_by_id(source.category_id) is None:
            raise ValueError("Category không tồn tại")
        if not source.link_selector:
            raise ValueError("Link selector không được để trống")
        self._validate_selectors(source)

    def create(self, source):
        self._validate(source)
        if self.repository.find_by_location(source.domain, source.path):
            raise ValueError("Nguồn tin với domain/path này đã tồn tại")
        return self.repository.create(source)

    def update(self, source):
        self._validate(source)
        if source.id is None:
            raise ValueError("Source ID là bắt buộc")
        duplicate = self.repository.find_by_location(source.domain, source.path)
        if duplicate and duplicate.id != source.id:
            raise ValueError("Nguồn tin với domain/path này đã tồn tại")
        return self.repository.update(source)

    def change_status(self, source_id, status):
        return self.repository.change_status(source_id, bool(status))

    def soft_delete(self, source_id):
        return self.repository.soft_delete(source_id)
