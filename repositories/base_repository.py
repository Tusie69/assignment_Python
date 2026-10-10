from abc import ABC, abstractmethod


class BaseRepository(ABC):
    """Hợp đồng CRUD chung cho các repository trong ứng dụng."""

    @abstractmethod
    def find_all(self, *args, **kwargs):
        pass

    @abstractmethod
    def find_by_id(self, entity_id):
        pass

    @abstractmethod
    def create(self, entity):
        pass

    @abstractmethod
    def update(self, entity):
        pass

    @abstractmethod
    def soft_delete(self, entity_id):
        pass
