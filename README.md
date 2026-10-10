# News Crawler Console

Ứng dụng Python 3 chạy trên Console để quản lý nguồn tin, thu thập bài viết và lưu vào MySQL.

## Chức năng

- Menu hai tầng đúng yêu cầu bài tập.
- CRUD nguồn tin; hỗ trợ Active/Inactive và xóa mềm.
- Danh sách bài viết có phân trang bằng `<` và `>`.
- Tìm kiếm trong tiêu đề, tóm tắt và nội dung.
- Lọc theo nguồn, ngày crawl hoặc kết hợp cả hai.
- Xem chi tiết và xóa mềm bài viết.
- Crawl VnExpress, Báo Thanh Niên và Báo Mới.
- Chống trùng bằng URL ở cả tầng ứng dụng và ràng buộc `UNIQUE` của MySQL.
- Tải trang chi tiết đồng thời bằng `ThreadPoolExecutor` (mặc định tối đa 5 luồng).
- Ghi nhật ký kết quả từng lần crawl.
- Xuất dữ liệu bài viết ra CSV hoặc JSON.

## Cấu trúc

```text
Crawl_me/
├── config/          # Cấu hình và kết nối MySQL
├── crawlers/        # BaseCrawler và crawler riêng cho từng báo
├── models/          # Các lớp dữ liệu
├── repositories/    # Tầng CRUD MySQL
├── services/        # Validation và logic nghiệp vụ
├── tests/           # Unit test không phụ thuộc mạng/DB
├── database.sql     # Cấu trúc bảng và dữ liệu ba nguồn mặc định
├── main.py          # Menu Console
└── requirements.txt
```

## Cài đặt

1. Tạo môi trường và cài thư viện:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Sao chép `.env.example` thành `.env`, sau đó nhập thông tin MySQL.

3. Import `database.sql` bằng phpMyAdmin, MySQL Workbench hoặc lệnh:

```bash
mysql -u root -p < database.sql
```

4. Chạy chương trình:

```bash
python main.py
```

5. Chạy kiểm thử:

```bash
python -m unittest discover -s tests -v
```

## Lưu ý khi crawl

- Mỗi lần chạy mặc định lấy tối đa 15 bài/nguồn và dùng tối đa 5 luồng.
- Không đặt số lượng quá lớn để tránh tạo tải không cần thiết cho website nguồn.
- CSS selector có thể thay đổi khi báo cập nhật giao diện. Có thể chỉnh selector tại menu quản lý nguồn; parser vẫn thử đọc Open Graph và JSON-LD khi dữ liệu CSS bị thiếu.
- Nội dung thu thập chỉ nên dùng cho mục đích học tập và demo, đồng thời giữ URL gốc của bài viết.

Các selector trong `database.sql` đã được kiểm tra với ba website ngày 10/10/2026.
