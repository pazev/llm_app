from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    Text,
    String,
    JSON,
)
from sqlalchemy.orm import relationship
from db.base import Base


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.conversation_id"),
        nullable=False,
    )
    sender = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    message_context = Column(JSON, nullable=True)
    datetime = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    conversation = relationship(
        "Conversation", back_populates="messages"
    )
    feedback = relationship(
        "MessageFeedback",
        back_populates="message",
        uselist=False,
        cascade="all, delete-orphan",
    )
