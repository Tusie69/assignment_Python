import re

from crawlers.generic_crawler import GenericCrawler


class BaoMoiCrawler(GenericCrawler):
    DEFAULT_SELECTORS = {
        "link_selector": "h3 a[href*='-c'][href$='.epi']",
        "title_selector": "h1",
        "description_selector": ".sapo",
        "content_selector": ".content-body",
        "remove_selector": "script, style, .related-news, .adsbygoogle",
        "image_selector": 'meta[property="og:image"]',
        "published_at_selector": "time[datetime]",
    }

    def _is_article_url(self, url):
        return super()._is_article_url(url) and bool(re.search(r"-c\d+\.epi$", url))
