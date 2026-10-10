class Article:
    def __init__(
        self,
        id=None,
        source_id=None,
        category_id=None,
        title=None,
        slug=None,
        url=None,
        description=None,
        content=None,
        image_url=None,
        author=None,
        published_at=None,
        crawled_at=None,
        is_rewrite=False,
        status=True,
        created_at=None,
        updated_at=None,
        deleted_at=None,
    ):
        self.id = id
        self.source_id = source_id
        self.category_id = category_id
        self.title = title
        self.slug = slug
        self.url = url
        self.description = description
        self.content = content
        self.image_url = image_url
        self.author = author
        self.published_at = published_at
        self.crawled_at = crawled_at
        self.is_rewrite = is_rewrite
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at

    def __str__(self):
        return f"{self.id} - {self.title} - {self.url}"
