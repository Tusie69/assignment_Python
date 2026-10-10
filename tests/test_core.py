import unittest

from bs4 import BeautifulSoup

from crawlers.baomoi_crawler import BaoMoiCrawler
from crawlers.crawler_factory import CrawlerFactory
from crawlers.generic_crawler import GenericCrawler
from crawlers.thanhnien_crawler import ThanhNienCrawler
from crawlers.vnexpress_crawler import VnExpressCrawler
from models.source import Source
from services.crawler_service import CrawlerService


class LocalCrawler(GenericCrawler):
    def __init__(self, source, pages):
        super().__init__(source, max_articles=5, max_workers=1)
        self.pages = pages

    def _get_soup(self, url):
        return BeautifulSoup(self.pages[url], "html.parser")


class CrawlerCoreTests(unittest.TestCase):
    def test_factory_uses_concrete_crawler(self):
        cases = (
            ("https://vnexpress.net", VnExpressCrawler),
            ("https://thanhnien.vn", ThanhNienCrawler),
            ("https://baomoi.com", BaoMoiCrawler),
            ("https://example.com", GenericCrawler),
        )
        for domain, expected_class in cases:
            source = Source(domain=domain)
            self.assertIsInstance(CrawlerFactory.create(source), expected_class)

    def test_slug_supports_vietnamese(self):
        self.assertEqual(
            CrawlerService._slug("Công nghệ Việt Nam: Đổi mới!"),
            "cong-nghe-viet-nam-doi-moi",
        )

    def test_date_supports_iso_and_vietnamese_text(self):
        iso_date = CrawlerService._date("2026-10-10T10:15:00.000Z")
        vietnamese_date = CrawlerService._date("Thứ bảy, 10/10/2026, 15:42 (GMT+7)")
        self.assertEqual(str(iso_date), "2026-10-10 17:15:00")
        self.assertEqual(str(vietnamese_date), "2026-10-10 15:42:00")

    def test_generic_crawler_extracts_detail(self):
        source = Source(
            domain="https://example.com",
            path="/news",
            link_selector="h3 a",
            title_selector="h1",
            description_selector=".summary",
            content_selector="article",
            published_at_selector="time",
        )
        pages = {
            "https://example.com/news": '<h3><a href="/post-1">Bài 1</a></h3>',
            "https://example.com/post-1": """
                <html><head><meta property="og:image" content="/image.jpg"></head>
                <body><h1>Tiêu đề thử nghiệm</h1><p class="summary">Tóm tắt</p>
                <time datetime="2026-10-10T08:00:00+07:00"></time>
                <article><p>Nội dung chi tiết của bài viết.</p></article></body></html>
            """,
        }
        articles = LocalCrawler(source, pages).crawl()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["title"], "Tiêu đề thử nghiệm")
        self.assertEqual(articles[0]["image_url"], "https://example.com/image.jpg")
        self.assertIn("Nội dung chi tiết", articles[0]["content"])


if __name__ == "__main__":
    unittest.main()
