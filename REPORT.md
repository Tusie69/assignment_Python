# Báo cáo kiến trúc News Crawler

## 1. Kiến trúc phân tầng

```text
Console Menu
    |
    v
Service (validation + nghiệp vụ)
    |-------------------------> CrawlerFactory -> BaseCrawler
    v                                      |-> VnExpressCrawler
Repository                                |-> ThanhNienCrawler
    |                                      |-> BaoMoiCrawler
    v
Database -> MySQL
```

- `models`: biểu diễn `Category`, `Source`, `Article`, `CrawlLog`.
- `repositories`: chỉ thực hiện truy vấn có tham số và ánh xạ dữ liệu.
- `services`: kiểm tra dữ liệu, điều phối CRUD và xử lý chống trùng.
- `crawlers`: áp dụng abstraction, kế thừa và đa hình cho từng nguồn báo.
- `main.py`: chỉ hiển thị menu, nhận input và gọi service.

## 2. Sơ đồ cơ sở dữ liệu

```text
categories (1) -------- (n) sources
     |                       |
     |                       +-------- (n) logs
     |
     +------------------ (n) articles (n) -------- (1) sources
```

- `articles.url` là duy nhất để chống lưu trùng.
- Các cột `source_id`, `category_id` là khóa ngoại và có index.
- `published_at`, `crawled_at` có index để hỗ trợ lọc/sắp xếp.
- Nguồn và bài viết dùng `deleted_at` để xóa mềm.

## 3. Luồng crawl

1. Đọc các nguồn `Active` từ MySQL.
2. `CrawlerFactory` chọn crawler theo domain.
3. Crawler tải trang danh sách, chuẩn hóa và loại URL trùng.
4. Các trang chi tiết được xử lý song song có giới hạn.
5. Parser lấy tiêu đề, tóm tắt, nội dung, ảnh, tác giả và ngày đăng.
6. Service kiểm tra URL trong database; bài không đổi được bỏ qua, bài thay đổi được cập nhật.
7. Kết quả được ghi vào bảng `logs` để phục vụ demo và kiểm tra lỗi.

## 4. Xử lý ngoại lệ

- Timeout, HTTP 4xx/5xx và lỗi từng bài không làm dừng toàn bộ nguồn.
- Selector sai được ghi vào thông báo crawl.
- Input số nguyên và ngày được kiểm tra trước khi gọi repository.
- Lỗi MySQL trả về kết quả an toàn và luôn đóng cursor/connection.
- Câu SQL sử dụng placeholder `%s`, không ghép dữ liệu người dùng vào truy vấn.
