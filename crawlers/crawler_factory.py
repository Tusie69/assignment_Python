from urllib.parse import urlparse

from crawlers.baomoi_crawler import BaoMoiCrawler
from crawlers.generic_crawler import GenericCrawler
from crawlers.thanhnien_crawler import ThanhNienCrawler
from crawlers.vnexpress_crawler import VnExpressCrawler


class CrawlerFactory:
    @staticmethod
    def create(source, **options):
        host = urlparse(source.domain).netloc.lower().removeprefix("www.")
        crawler_classes = {
            "vnexpress.net": VnExpressCrawler,
            "thanhnien.vn": ThanhNienCrawler,
            "baomoi.com": BaoMoiCrawler,
        }
        crawler_class = crawler_classes.get(host, GenericCrawler)
        return crawler_class(source, **options)
