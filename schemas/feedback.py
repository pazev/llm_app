from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class FeedbackSubmit(BaseModel):
    message_id: int
    positive_feedback: bool
    comment: str

    @field_validator("comment")
    @classmethod
    def comment_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("comment must not be empty")
        return v.strip()


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message_feedback_id: int
    message_id: int
    positive_feedback: Optional[bool] = None
    comment: Optional[str] = None
    datetime: datetime
