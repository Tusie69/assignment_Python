class Category:
    def __init__(
        self,
        id=None,
        name=None,
        description=None,
        alias=None,
        slug=None,
        created_at=None,
        updated_at=None,
        deleted_at=None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.alias = alias
        self.slug = slug
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at

    def __str__(self):
        return f"{self.id} - {self.name} - {self.slug}"