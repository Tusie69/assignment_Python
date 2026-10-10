class Source:
    def __init__(
        self,
        id=None,
        name=None,
        domain=None,
        path=None,
        category_id=None,
        description=None,
        status=True,
        link_selector=None,
        title_selector=None,
        description_selector=None,
        content_selector=None,
        comment_selector=None,
        remove_selector=None,
        image_selector=None,
        author_selector=None,
        published_at_selector=None,
        created_at=None,
        updated_at=None,
        deleted_at=None
    ):
        self.id = id
        self.name = name
        self.domain = domain
        self.path = path
        self.category_id = category_id
        self.description = description
        self.status = status

        self.link_selector = link_selector
        self.title_selector = title_selector
        self.description_selector = description_selector
        self.content_selector = content_selector
        self.comment_selector = comment_selector
        self.remove_selector = remove_selector
        self.image_selector = image_selector
        self.author_selector = author_selector
        self.published_at_selector = published_at_selector

        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at

    def __str__(self):
        return f"{self.id} - {self.name} - {self.domain}{self.path or ''}"