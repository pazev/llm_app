from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ConversationCreate(BaseModel):
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conversation_id: int
    datetime_start: datetime
    title: Optional[str] = None


class ConversationSummary(BaseModel):
    conversation_id: int
    datetime_start: datetime
    title: Optional[str] = None
    message_count: int
    feedback_count: int
