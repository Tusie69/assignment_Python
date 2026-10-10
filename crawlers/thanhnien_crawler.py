import re

from crawlers.generic_crawler import GenericCrawler


class ThanhNienCrawler(GenericCrawler):
    DEFAULT_SELECTORS = {
        "link_selector": "a.box-category-link-title[href]",
        "title_selector": "h1.detail-title",
        "description_selector": ".detail-sapo",
        "content_selector": ".detail-content",
        "remove_selector": "script, style, .detail-related, .adsbygoogle",
        "image_selector": 'meta[property="og:image"]',
        "author_selector": ".detail-author",
        "published_at_selector": "time[datetime]",
    }

    def _is_article_url(self, url):
        return super()._is_article_url(url) and bool(re.search(r"-\d+\.htm$", url))
