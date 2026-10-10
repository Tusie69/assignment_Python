import re
import unicodedata
from datetime import datetime, timedelta, timezone

from crawlers.crawler_factory import CrawlerFactory
from models.article import Article
from models.crawl_log import CrawlLog
from repositories.article_repository import ArticleRepository
from repositories.log_repository import LogRepository
from repositories.source_repository import SourceRepository


class CrawlerService:
    def __init__(self, source_repository=None, article_repository=None, log_repository=None):
        self.source_repository = source_repository or SourceRepository()
        self.article_repository = article_repository or ArticleRepository()
        self.log_repository = log_repository or LogRepository()

    @staticmethod
    def _slug(value):
        normalized = unicodedata.normalize("NFD", value or "")
        without_accents = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
        without_accents = without_accents.replace("đ", "d").replace("Đ", "D")
        slug = re.sub(r"[^a-z0-9]+", "-", without_accents.lower()).strip("-")
        return (slug or "article")[:500]

    @staticmethod
    def _date(value):
        if not value:
            return None
        if isinstance(value, datetime):
            parsed = value
        else:
            text = str(value).strip()
            parsed = None
            try:
                parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                match = re.search(r"(\d{1,2})[/.](\d{1,2})[/.](\d{4}).*?(\d{1,2}):(\d{2})", text)
                if match:
                    day, month, year, hour, minute = map(int, match.groups())
                    parsed = datetime(year, month, day, hour, minute)
                else:
                    for pattern in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                        try:
                            parsed = datetime.strptime(text, pattern)
                            break
                        except ValueError:
                            continue
            if parsed is None:
                return None

        if parsed.tzinfo:
            vietnam_timezone = timezone(timedelta(hours=7))
            parsed = parsed.astimezone(vietnam_timezone).replace(tzinfo=None)
        return parsed

    def _run_source(self, source, max_articles=15, max_workers=5):
        log = CrawlLog(
            source_id=source.id,
            action="CRAWL",
            status="RUNNING",
            started_at=datetime.now(),
        )
        self.log_repository.create(log)

        try:
            crawler = CrawlerFactory.create(
                source,
                max_articles=max_articles,
                max_workers=max_workers,
            )
            crawled = crawler.crawl()
            log.total_articles = len(crawled) + len(crawler.errors)

            for item in crawled:
                article = Article(
                    source_id=source.id,
                    category_id=source.category_id,
                    title=(item.get("title") or "").strip(),
                    slug=self._slug(item.get("title")),
                    url=item.get("url"),
                    description=item.get("description"),
                    content=item.get("content"),
                    image_url=item.get("image_url"),
                    author=item.get("author"),
                    published_at=self._date(item.get("published_at")),
                    crawled_at=item.get("crawled_at") or datetime.now(),
                    status=True,
                )
                if not article.url or not article.title or not article.content:
                    log.skipped_articles += 1
                    continue

                existing = self.article_repository.find_by_url(article.url)
                unchanged = (
                    existing
                    and existing.deleted_at is None
                    and existing.title == article.title
                    and existing.description == article.description
                    and existing.content == article.content
                )
                if unchanged:
                    log.skipped_articles += 1
                elif existing:
                    article.id = existing.id
                    if self.article_repository.update(article):
                        log.updated_articles += 1
                    else:
                        log.skipped_articles += 1
                elif self.article_repository.create(article):
                    log.new_articles += 1
                else:
                    log.skipped_articles += 1

            log.skipped_articles += len(crawler.errors)
            log.status = "SUCCESS" if crawled else "FAILED"
            if crawler.errors:
                examples = " | ".join(crawler.errors[:3])
                log.message = f"Có {len(crawler.errors)} bài lỗi. {examples}"[:2000]
            if not crawled and not log.message:
                log.message = "Không thu thập được bài viết hợp lệ."
        except Exception as error:
            log.status = "FAILED"
            log.message = str(error)[:2000]
        finally:
            log.finished_at = datetime.now()
            if log.id:
                self.log_repository.update(log)
        return log

    def crawl_source(self, source_id, max_articles=15, max_workers=5):
        source = self.source_repository.find_by_id(source_id)
        if source is None:
            raise ValueError("Nguồn tin không tồn tại")
        if not source.status:
            raise ValueError("Nguồn tin đang ở trạng thái Inactive")
        return self._run_source(source, max_articles, max_workers)

    def crawl_active_sources(self, max_articles=15, max_workers=5):
        sources = self.source_repository.find_active()
        if not sources:
            raise ValueError("Không có nguồn tin Active")
        return [
            self._run_source(source, max_articles, max_workers)
            for source in sources
        ]
