from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, field_validator


class SenderEnum(str, Enum):
    user = "user"
    llm = "llm"


class MessageCreate(BaseModel):
    conversation_id: int
    sender: SenderEnum
    content: str

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("content must not be empty")
        return v


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message_id: int
    conversation_id: int
    sender: str
    content: str
    datetime: datetime
