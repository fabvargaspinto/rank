from backend.core.share.domain.date import Date
from datetime import datetime

class CommentCreatedAt (Date):
    def __init__(self, value: datetime):
        super().__init__(value)