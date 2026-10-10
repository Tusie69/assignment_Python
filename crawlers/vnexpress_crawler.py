import re

from crawlers.generic_crawler import GenericCrawler


class VnExpressCrawler(GenericCrawler):
    DEFAULT_SELECTORS = {
        "link_selector": "h3.title-news a[href]",
        "title_selector": "h1.title-detail",
        "description_selector": ".description",
        "content_selector": "article.fck_detail",
        "remove_selector": "script, style, .box-tinlienquanv2, .banner-ads",
        "image_selector": 'meta[property="og:image"]',
        "author_selector": ".author_mail, .author",
        "published_at_selector": ".date",
    }

    def _is_article_url(self, url):
        return super()._is_article_url(url) and bool(re.search(r"-\d+\.html$", url))
