from models.category import Category
from repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, repository=None):
        self.repository = repository or CategoryRepository()

    def find_all(self):
        return self.repository.find_all()

    def find_by_id(self, category_id):
        return self.repository.find_by_id(category_id)

    def create(self, category):
        if not isinstance(category, Category):
            raise ValueError("Category không hợp lệ")
        if not category.name or not category.name.strip():
            raise ValueError("Tên category không được để trống")
        if not category.slug or not category.slug.strip():
            raise ValueError("Slug không được để trống")
        return self.repository.create(category)

    def update(self, category):
        if not isinstance(category, Category):
            raise ValueError("Category không hợp lệ")
        if not category.name or not category.name.strip():
            raise ValueError("Tên category không được để trống")
        if not category.slug or not category.slug.strip():
            raise ValueError("Slug không được để trống")
        if category.id is None:
            raise ValueError("Category ID là bắt buộc")
        return self.repository.update(category)

    def soft_delete(self, category_id):
        return self.repository.soft_delete(category_id)
