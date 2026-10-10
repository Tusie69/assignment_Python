class CrawlLog:
    def __init__(
        self,
        id=None,
        source_id=None,
        action=None,
        status=None,
        message=None,
        total_articles=0,
        new_articles=0,
        updated_articles=0,
        skipped_articles=0,
        started_at=None,
        finished_at=None,
        created_at=None,
    ):
        self.id = id
        self.source_id = source_id
        self.action = action
        self.status = status
        self.message = message
        self.total_articles = total_articles
        self.new_articles = new_articles
        self.updated_articles = updated_articles
        self.skipped_articles = skipped_articles
        self.started_at = started_at
        self.finished_at = finished_at
        self.created_at = created_at
