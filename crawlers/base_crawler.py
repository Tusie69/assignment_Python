from abc import ABC, abstractmethod


class BaseCrawler(ABC):
    """Hợp đồng chung cho crawler của từng nguồn báo."""

    def __init__(self, source, timeout=20, max_articles=15, max_workers=5):
        self.source = source
        self.timeout = timeout
        self.max_articles = max(1, int(max_articles))
        self.max_workers = max(1, int(max_workers))
        self.errors = []

    @abstractmethod
    def discover_links(self):
        pass

    @abstractmethod
    def parse_article(self, url):
        pass

    @abstractmethod
    def crawl(self):
        pass
