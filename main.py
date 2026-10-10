import math
from textwrap import shorten

from config.database import Database
from models.source import Source
from services.article_service import ArticleService
from services.category_service import CategoryService
from services.crawler_service import CrawlerService
from services.source_service import SourceService


PAGE_SIZE = 10


class NewsCrawlerApp:
    def __init__(self):
        self.database = Database()
        self.source_service = SourceService()
        self.category_service = CategoryService()
        self.article_service = ArticleService()
        self.crawler_service = CrawlerService()

    @staticmethod
    def read_int(prompt, allow_empty=False, minimum=None):
        while True:
            raw_value = input(prompt).strip()
            if allow_empty and not raw_value:
                return None
            try:
                value = int(raw_value)
                if minimum is not None and value < minimum:
                    print(f"Giá trị phải lớn hơn hoặc bằng {minimum}.")
                    continue
                return value
            except ValueError:
                print("Vui lòng nhập số nguyên hợp lệ.")

    @staticmethod
    def keep_value(label, current):
        value = input(f"{label} [{current or ''}]: ").strip()
        return value if value else current

    @staticmethod
    def compact(value, width):
        text = str(value or "-").replace("\n", " ")
        return shorten(text, width=width, placeholder="...")

    def show_categories(self):
        categories = self.category_service.find_all()
        print("\nDanh mục:")
        for category in categories:
            print(f"  {category.id}. {category.name} ({category.slug})")
        return categories

    def show_sources(self):
        sources = self.source_service.find_all()
        print("\nID  TÊN NGUỒN                URL                                      TRẠNG THÁI")
        print("-" * 92)
        for source in sources:
            url = f"{source.domain}{source.path or ''}"
            status = "Active" if source.status else "Inactive"
            print(f"{source.id:<3} {self.compact(source.name, 25):<25} {self.compact(url, 40):<40} {status}")
        if not sources:
            print("Chưa có nguồn tin.")
        return sources

    def input_source(self):
        self.show_categories()
        return Source(
            name=input("Tên nguồn: ").strip(),
            domain=input("Domain (ví dụ https://example.com): ").strip(),
            path=input("Path trang danh sách (ví dụ /tin-moi): ").strip(),
            category_id=self.read_int("Category ID: ", minimum=1),
            description=input("Mô tả: ").strip() or None,
            status=True,
            link_selector=input("CSS selector lấy link bài viết: ").strip(),
            title_selector=input("CSS selector tiêu đề: ").strip() or None,
            description_selector=input("CSS selector tóm tắt: ").strip() or None,
            content_selector=input("CSS selector nội dung: ").strip() or None,
            remove_selector=input("CSS selector phần cần loại bỏ: ").strip() or None,
            image_selector=input("CSS selector ảnh: ").strip() or None,
            author_selector=input("CSS selector tác giả: ").strip() or None,
            published_at_selector=input("CSS selector ngày đăng: ").strip() or None,
        )

    def update_source(self):
        source_id = self.read_int("Source ID cần cập nhật: ", minimum=1)
        source = self.source_service.find_by_id(source_id)
        if source is None:
            print("Không tìm thấy nguồn tin.")
            return

        self.show_categories()
        source.name = self.keep_value("Tên", source.name)
        source.domain = self.keep_value("Domain", source.domain)
        source.path = self.keep_value("Path", source.path)
        category_id = self.read_int(
            f"Category ID [{source.category_id}] (Enter để giữ): ",
            allow_empty=True,
            minimum=1,
        )
        source.category_id = category_id or source.category_id
        source.description = self.keep_value("Mô tả", source.description)
        source.link_selector = self.keep_value("Link selector", source.link_selector)
        source.title_selector = self.keep_value("Title selector", source.title_selector)
        source.description_selector = self.keep_value("Description selector", source.description_selector)
        source.content_selector = self.keep_value("Content selector", source.content_selector)
        source.remove_selector = self.keep_value("Remove selector", source.remove_selector)
        source.image_selector = self.keep_value("Image selector", source.image_selector)
        source.author_selector = self.keep_value("Author selector", source.author_selector)
        source.published_at_selector = self.keep_value("Published selector", source.published_at_selector)
        print("Đã cập nhật nguồn tin." if self.source_service.update(source) else "Cập nhật thất bại.")

    def source_menu(self):
        while True:
            print("\n--- QUẢN LÝ NGUỒN TIN ---")
            print("1.1. Xem danh sách nguồn tin")
            print("1.2. Thêm nguồn tin mới")
            print("1.3. Cập nhật nguồn tin")
            print("1.4. Kích hoạt/Bỏ kích hoạt nguồn tin")
            print("1.5. Xóa mềm nguồn tin")
            print("0. Quay lại Menu chính")
            choice = input("Chọn: ").strip()
            try:
                if choice in ("1", "1.1"):
                    self.show_sources()
                elif choice in ("2", "1.2"):
                    source = self.input_source()
                    print("Đã thêm nguồn tin." if self.source_service.create(source) else "Thêm thất bại.")
                elif choice in ("3", "1.3"):
                    self.update_source()
                elif choice in ("4", "1.4"):
                    source_id = self.read_int("Source ID: ", minimum=1)
                    source = self.source_service.find_by_id(source_id)
                    if not source:
                        print("Không tìm thấy nguồn tin.")
                    else:
                        new_status = not bool(source.status)
                        changed = self.source_service.change_status(source_id, new_status)
                        print(f"Đã chuyển sang {'Active' if new_status else 'Inactive'}." if changed else "Thay đổi thất bại.")
                elif choice in ("5", "1.5"):
                    source_id = self.read_int("Source ID cần xóa mềm: ", minimum=1)
                    confirm = input("Nhập YES để xác nhận: ").strip().upper()
                    if confirm == "YES":
                        print("Đã xóa mềm." if self.source_service.soft_delete(source_id) else "Xóa thất bại.")
                elif choice == "0":
                    return
                else:
                    print("Lựa chọn không hợp lệ.")
            except ValueError as error:
                print(f"Lỗi: {error}")

    def print_articles(self, articles):
        print("\nID     TIÊU ĐỀ                                                     SOURCE  NGÀY ĐĂNG")
        print("-" * 100)
        for article in articles:
            published = article.published_at.strftime("%d/%m/%Y %H:%M") if article.published_at else "-"
            print(f"{article.id:<6} {self.compact(article.title, 60):<60} {article.source_id:<7} {published}")
        if not articles:
            print("Không có bài viết phù hợp.")

    def paginate(self, fetch_page, count_items, title):
        total = count_items()
        if total == 0:
            self.print_articles([])
            return
        total_pages = max(1, math.ceil(total / PAGE_SIZE))
        page = 1
        while True:
            page = min(page, total_pages)
            print(f"\n{title} - Trang {page}/{total_pages} - Tổng {total} bài")
            self.print_articles(fetch_page(page, PAGE_SIZE))
            command = input("Nhập > trang sau, < trang trước, q quay lại: ").strip().lower()
            if command == ">":
                if page < total_pages:
                    page += 1
                else:
                    print("Đang ở trang cuối.")
            elif command == "<":
                if page > 1:
                    page -= 1
                else:
                    print("Đang ở trang đầu.")
            elif command == "q":
                return
            else:
                print("Lệnh điều hướng không hợp lệ.")

    def show_article_detail(self):
        article_id = self.read_int("Article ID: ", minimum=1)
        article = self.article_service.find_by_id(article_id)
        if article is None:
            print("Không tìm thấy bài viết.")
            return
        print("\n" + "=" * 80)
        print(f"TIÊU ĐỀ: {article.title}")
        print(f"TÓM TẮT: {article.description or '-'}")
        print(f"TÁC GIẢ: {article.author or '-'}")
        print(f"NGÀY ĐĂNG: {article.published_at or '-'}")
        print(f"URL GỐC: {article.url}")
        print("-" * 80)
        print(article.content or "Không có nội dung.")
        print("=" * 80)

    def article_menu(self):
        while True:
            print("\n--- QUẢN LÝ TIN TỨC ---")
            print("2.1. Xem danh sách tin tức")
            print("2.2. Tìm kiếm theo tiêu đề/nội dung")
            print("2.3. Lọc theo nguồn và/hoặc ngày crawl")
            print("2.4. Xem chi tiết bài viết")
            print("2.5. Xóa bài viết")
            print("2.6. Xuất danh sách ra CSV/JSON")
            print("0. Quay lại Menu chính")
            choice = input("Chọn: ").strip()
            try:
                if choice in ("1", "2.1"):
                    self.paginate(self.article_service.find_all, self.article_service.count_all, "DANH SÁCH TIN")
                elif choice in ("2", "2.2"):
                    keyword = input("Từ khóa: ").strip()
                    self.paginate(
                        lambda page, size: self.article_service.search(keyword, page, size),
                        lambda: self.article_service.count_search(keyword),
                        f"KẾT QUẢ TÌM '{keyword}'",
                    )
                elif choice in ("3", "2.3"):
                    self.show_sources()
                    source_id = self.read_int("Source ID (Enter để bỏ qua): ", allow_empty=True, minimum=1)
                    crawled_date = input("Ngày crawl YYYY-MM-DD (Enter để bỏ qua): ").strip() or None
                    if source_id is None and crawled_date is None:
                        raise ValueError("Cần nhập Source ID hoặc ngày crawl")
                    self.paginate(
                        lambda page, size: self.article_service.filter(source_id, crawled_date, page, size),
                        lambda: self.article_service.count_filter(source_id, crawled_date),
                        "KẾT QUẢ LỌC",
                    )
                elif choice in ("4", "2.4"):
                    self.show_article_detail()
                elif choice in ("5", "2.5"):
                    article_id = self.read_int("Article ID cần xóa: ", minimum=1)
                    confirm = input("Nhập YES để xác nhận: ").strip().upper()
                    if confirm == "YES":
                        print("Đã xóa bài viết." if self.article_service.soft_delete(article_id) else "Xóa thất bại.")
                elif choice in ("6", "2.6"):
                    file_format = input("Định dạng (csv/json): ").strip().lower()
                    path, total = self.article_service.export(file_format)
                    print(f"Đã xuất {total} bài viết ra: {path.resolve()}")
                elif choice == "0":
                    return
                else:
                    print("Lựa chọn không hợp lệ.")
            except ValueError as error:
                print(f"Lỗi: {error}")

    @staticmethod
    def print_crawl_log(log):
        print(
            f"Source #{log.source_id}: {log.status} | Tổng {log.total_articles} | "
            f"Mới {log.new_articles} | Cập nhật {log.updated_articles} | "
            f"Bỏ qua/lỗi {log.skipped_articles}"
        )
        if log.message:
            print(f"  Chi tiết: {log.message}")

    def crawler_menu(self):
        while True:
            print("\n--- CHẠY CRAWLER ---")
            print("3.1. Crawl tất cả nguồn Active")
            print("3.2. Crawl một nguồn cụ thể")
            print("0. Quay lại Menu chính")
            choice = input("Chọn: ").strip()
            try:
                if choice in ("1", "3.1"):
                    limit = self.read_int("Số bài tối đa mỗi nguồn [15]: ", allow_empty=True, minimum=1) or 15
                    print("Đang crawl các nguồn Active...")
                    for log in self.crawler_service.crawl_active_sources(limit, 5):
                        self.print_crawl_log(log)
                elif choice in ("2", "3.2"):
                    self.show_sources()
                    source_id = self.read_int("Source ID: ", minimum=1)
                    limit = self.read_int("Số bài tối đa [15]: ", allow_empty=True, minimum=1) or 15
                    print("Đang crawl dữ liệu...")
                    self.print_crawl_log(self.crawler_service.crawl_source(source_id, limit, 5))
                elif choice == "0":
                    return
                else:
                    print("Lựa chọn không hợp lệ.")
            except ValueError as error:
                print(f"Lỗi: {error}")

    def run(self):
        if not self.database.test_connection():
            print("Không thể kết nối MySQL. Hãy kiểm tra file .env và import database.sql.")
            return
        while True:
            print("\n=== CHƯƠNG TRÌNH TỔNG HỢP TIN TỨC ĐA NGUỒN ===")
            print("1. Quản lý nguồn tin (Source Management)")
            print("2. Quản lý tin tức (News Article Management)")
            print("3. Chạy Crawler (Crawl Data)")
            print("0. Thoát chương trình")
            choice = input("Chọn: ").strip()
            if choice == "1":
                self.source_menu()
            elif choice == "2":
                self.article_menu()
            elif choice == "3":
                self.crawler_menu()
            elif choice == "0":
                print("Tạm biệt!")
                return
            else:
                print("Lựa chọn không hợp lệ.")


if __name__ == "__main__":
    NewsCrawlerApp().run()
