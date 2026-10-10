CREATE DATABASE IF NOT EXISTS crawler_me
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE crawler_me;

CREATE TABLE IF NOT EXISTS categories (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500) NULL,
    alias VARCHAR(100) NULL,
    slug VARCHAR(150) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    CONSTRAINT uq_categories_slug UNIQUE (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sources (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    path VARCHAR(255) NULL,
    category_id INT UNSIGNED NOT NULL,
    description VARCHAR(500) NULL,
    status TINYINT(1) NOT NULL DEFAULT 1,
    link_selector VARCHAR(500) NOT NULL,
    title_selector VARCHAR(500) NULL,
    description_selector VARCHAR(500) NULL,
    content_selector VARCHAR(500) NULL,
    comment_selector VARCHAR(500) NULL,
    remove_selector VARCHAR(1000) NULL,
    image_selector VARCHAR(500) NULL,
    author_selector VARCHAR(500) NULL,
    published_at_selector VARCHAR(500) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    INDEX idx_sources_status (status, deleted_at),
    INDEX idx_sources_category_id (category_id),
    CONSTRAINT fk_sources_category
        FOREIGN KEY (category_id) REFERENCES categories(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS articles (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    source_id INT UNSIGNED NOT NULL,
    category_id INT UNSIGNED NOT NULL,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) NULL,
    url VARCHAR(768) NOT NULL,
    description TEXT NULL,
    content LONGTEXT NULL,
    image_url VARCHAR(1000) NULL,
    author VARCHAR(255) NULL,
    published_at DATETIME NULL,
    crawled_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_rewrite TINYINT(1) NOT NULL DEFAULT 0,
    status TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    CONSTRAINT uq_articles_url UNIQUE (url),
    INDEX idx_articles_source_id (source_id),
    INDEX idx_articles_category_id (category_id),
    INDEX idx_articles_published_at (published_at),
    INDEX idx_articles_crawled_at (crawled_at),
    INDEX idx_articles_source_crawled (source_id, crawled_at),
    CONSTRAINT fk_articles_source
        FOREIGN KEY (source_id) REFERENCES sources(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_articles_category
        FOREIGN KEY (category_id) REFERENCES categories(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    source_id INT UNSIGNED NOT NULL,
    action VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    message TEXT NULL,
    total_articles INT UNSIGNED NOT NULL DEFAULT 0,
    new_articles INT UNSIGNED NOT NULL DEFAULT 0,
    updated_articles INT UNSIGNED NOT NULL DEFAULT 0,
    skipped_articles INT UNSIGNED NOT NULL DEFAULT 0,
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_logs_source_id (source_id),
    INDEX idx_logs_started_at (started_at),
    CONSTRAINT fk_logs_source
        FOREIGN KEY (source_id) REFERENCES sources(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO categories (name, description, alias, slug)
SELECT 'Tin tổng hợp', 'Tin tức tổng hợp từ các nguồn báo', 'general', 'tin-tong-hop'
WHERE NOT EXISTS (
    SELECT 1 FROM categories WHERE slug = 'tin-tong-hop'
);

SET @general_category_id = (
    SELECT id FROM categories WHERE slug = 'tin-tong-hop' LIMIT 1
);

UPDATE sources
SET name = 'VnExpress', path = '/thoi-su', category_id = @general_category_id,
    description = 'Tin tức mới từ VnExpress', status = 1,
    link_selector = 'h3.title-news a[href]',
    title_selector = 'h1.title-detail',
    description_selector = '.description',
    content_selector = 'article.fck_detail',
    remove_selector = 'script, style, .box-tinlienquanv2, .banner-ads',
    image_selector = 'meta[property="og:image"]',
    author_selector = '.author_mail, .author',
    published_at_selector = '.date', deleted_at = NULL
WHERE domain = 'https://vnexpress.net';

INSERT INTO sources (
    name, domain, path, category_id, description, status,
    link_selector, title_selector, description_selector, content_selector,
    remove_selector, image_selector, author_selector, published_at_selector
)
SELECT
    'VnExpress', 'https://vnexpress.net', '/thoi-su', @general_category_id,
    'Tin tức mới từ VnExpress', 1,
    'h3.title-news a[href]', 'h1.title-detail', '.description',
    'article.fck_detail', 'script, style, .box-tinlienquanv2, .banner-ads',
    'meta[property="og:image"]', '.author_mail, .author', '.date'
WHERE NOT EXISTS (
    SELECT 1 FROM sources WHERE domain = 'https://vnexpress.net' AND deleted_at IS NULL
);

INSERT INTO sources (
    name, domain, path, category_id, description, status,
    link_selector, title_selector, description_selector, content_selector,
    remove_selector, image_selector, author_selector, published_at_selector
)
SELECT
    'Báo Thanh Niên', 'https://thanhnien.vn', '/', @general_category_id,
    'Tin tức mới từ Báo Thanh Niên', 1,
    'a.box-category-link-title[href]', 'h1.detail-title', '.detail-sapo',
    '.detail-content', 'script, style, .detail-related, .adsbygoogle',
    'meta[property="og:image"]', '.detail-author', 'time[datetime]'
WHERE NOT EXISTS (
    SELECT 1 FROM sources WHERE domain = 'https://thanhnien.vn' AND deleted_at IS NULL
);

INSERT INTO sources (
    name, domain, path, category_id, description, status,
    link_selector, title_selector, description_selector, content_selector,
    remove_selector, image_selector, author_selector, published_at_selector
)
SELECT
    'Báo Mới', 'https://baomoi.com', '/tin-moi.epi', @general_category_id,
    'Tin tức mới được tổng hợp trên Báo Mới', 1,
    'h3 a[href*="-c"][href$=".epi"]', 'h1', '.sapo',
    '.content-body', 'script, style, .related-news, .adsbygoogle',
    'meta[property="og:image"]', NULL, 'time[datetime]'
WHERE NOT EXISTS (
    SELECT 1 FROM sources WHERE domain = 'https://baomoi.com' AND deleted_at IS NULL
);
