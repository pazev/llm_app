from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator


class FeedbackSubmit(BaseModel):
    message_id: int
    positive_feedback: Optional[bool] = None
    comment: Optional[str] = None

    @model_validator(mode="after")
    def at_least_one_field(self):
        if self.positive_feedback is None and self.comment is None:
            raise ValueError("at least one of positive_feedback or comment must be provided")
        return self


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message_feedback_id: int
    message_id: int
    positive_feedback: Optional[bool] = None
    comment: Optional[str] = None
    datetime: datetime
