from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ConversationCreate(BaseModel):
    title: Optional[str] = None
    resumed_from_conversation_id: Optional[int] = None


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conversation_id: int
    datetime_start: datetime
    title: Optional[str] = None
    resumed_from_conversation_id: Optional[int] = None


class ConversationSummary(BaseModel):
    conversation_id: int
    datetime_start: datetime
    title: Optional[str] = None
    message_count: int
    feedback_count: int
    resumed_from_conversation_id: Optional[int] = None
    token_usage: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    username: Optional[str] = None
