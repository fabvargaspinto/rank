from backend.core.share.domain.uuid import UUID

class CommentId (UUID):

    def __init__(self, value: str):
        self.value = value
        self.validate()

  