import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

from crawlers.base_crawler import BaseCrawler


class GenericCrawler(BaseCrawler):
    """Crawler theo CSS selector, đồng thời có fallback bằng metadata."""

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129 Safari/537.36"
    )
    DEFAULT_SELECTORS = {}

    def __init__(self, source, timeout=20, max_articles=15, max_workers=5):
        super().__init__(source, timeout, max_articles, max_workers)
        self._local = threading.local()

    def _session(self):
        if not hasattr(self._local, "session"):
            session = requests.Session()
            session.headers.update({
                "User-Agent": self.USER_AGENT,
                "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.7",
            })
            self._local.session = session
        return self._local.session

    def _get_soup(self, url):
        response = self._session().get(url, timeout=self.timeout)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def _selector(self, name):
        configured = getattr(self.source, name, None)
        return configured or self.DEFAULT_SELECTORS.get(name)

    @staticmethod
    def _text(node):
        return node.get_text(" ", strip=True) if node else None

    @staticmethod
    def _normalize_url(url):
        parsed = urlparse(url)
        path = re.sub(r"/{2,}", "/", parsed.path)
        return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", "", ""))

    def _select_one(self, soup, selector):
        if not selector:
            return None
        try:
            return soup.select_one(selector)
        except Exception as error:
            self.errors.append(f"Selector không hợp lệ '{selector}': {error}")
            return None

    def _node_value(self, soup, selector, attributes=()):
        node = self._select_one(soup, selector)
        if not node:
            return None
        for attribute in attributes:
            value = node.get(attribute)
            if value:
                return value.strip()
        return self._text(node)

    @staticmethod
    def _meta(soup, key):
        node = soup.select_one(f'meta[property="{key}"]') or soup.select_one(f'meta[name="{key}"]')
        return node.get("content", "").strip() if node else None

    @staticmethod
    def _json_article(soup):
        def find_article(value):
            if isinstance(value, dict):
                item_type = value.get("@type")
                if item_type in ("Article", "NewsArticle", "ReportageNewsArticle"):
                    return value
                for nested in value.values():
                    found = find_article(nested)
                    if found:
                        return found
            elif isinstance(value, list):
                for nested in value:
                    found = find_article(nested)
                    if found:
                        return found
            return None

        for node in soup.select('script[type="application/ld+json"]'):
            try:
                found = find_article(json.loads(node.string or node.get_text()))
                if found:
                    return found
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
        return {}

    @staticmethod
    def _author_from_json(value):
        if isinstance(value, dict):
            return value.get("name")
        if isinstance(value, list):
            names = [GenericCrawler._author_from_json(item) for item in value]
            return ", ".join(name for name in names if name) or None
        return value if isinstance(value, str) else None

    def _is_article_url(self, url):
        source_host = urlparse(self.source.domain).netloc.removeprefix("www.")
        target_host = urlparse(url).netloc.removeprefix("www.")
        return target_host == source_host

    def discover_links(self):
        listing_url = urljoin(self.source.domain.rstrip("/") + "/", self.source.path or "")
        soup = self._get_soup(listing_url)
        selector = self._selector("link_selector") or "a[href]"
        try:
            nodes = soup.select(selector)
        except Exception as error:
            raise ValueError(f"Link selector không hợp lệ '{selector}': {error}") from error

        links = []
        seen = set()
        for node in nodes:
            href = node.get("href")
            if not href:
                continue
            url = self._normalize_url(urljoin(listing_url, href))
            if url not in seen and self._is_article_url(url):
                seen.add(url)
                links.append(url)
            if len(links) >= self.max_articles:
                break
        return links

    def _content(self, soup):
        node = self._select_one(soup, self._selector("content_selector"))
        if not node:
            return None
        remove_selector = self._selector("remove_selector")
        if remove_selector:
            try:
                for unwanted in node.select(remove_selector):
                    unwanted.decompose()
            except Exception as error:
                self.errors.append(f"Remove selector không hợp lệ: {error}")
        return node.get_text("\n", strip=True)

    def parse_article(self, url):
        soup = self._get_soup(url)
        structured = self._json_article(soup)
        canonical = self._node_value(soup, 'link[rel="canonical"]', ("href",)) or url
        image = (
            self._node_value(
                soup,
                self._selector("image_selector"),
                ("content", "src", "data-src", "data-original"),
            )
            or self._meta(soup, "og:image")
            or structured.get("image")
        )
        if isinstance(image, list):
            image = image[0] if image else None
        if isinstance(image, dict):
            image = image.get("url")

        title = (
            self._node_value(soup, self._selector("title_selector"))
            or self._meta(soup, "og:title")
            or structured.get("headline")
        )
        description = (
            self._node_value(soup, self._selector("description_selector"))
            or self._meta(soup, "og:description")
            or structured.get("description")
        )
        author = (
            self._node_value(soup, self._selector("author_selector"))
            or self._author_from_json(structured.get("author"))
            or self._meta(soup, "author")
        )
        published_at = (
            self._node_value(soup, self._selector("published_at_selector"), ("datetime", "content"))
            or self._meta(soup, "article:published_time")
            or structured.get("datePublished")
        )
        return {
            "url": self._normalize_url(urljoin(url, canonical)),
            "title": title,
            "description": description,
            "content": self._content(soup),
            "image_url": urljoin(url, image) if image else None,
            "author": author,
            "published_at": published_at,
            "crawled_at": datetime.now(),
        }

    def crawl(self):
        links = self.discover_links()
        if not links:
            raise ValueError("Không tìm thấy đường dẫn bài viết. Hãy kiểm tra link selector.")

        articles = []
        workers = min(self.max_workers, len(links))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(self.parse_article, url): url for url in links}
            for future in as_completed(futures):
                url = futures[future]
                try:
                    article = future.result()
                    if article.get("title") and article.get("content"):
                        articles.append(article)
                    else:
                        self.errors.append(f"Thiếu tiêu đề hoặc nội dung: {url}")
                except Exception as error:
                    self.errors.append(f"{url}: {error}")
        return articles
