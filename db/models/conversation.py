from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from db.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id = Column(
        Integer, primary_key=True, index=True
    )
    datetime_start = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    title = Column(String(255), nullable=True)
    resumed_from_conversation_id = Column(
        Integer,
        ForeignKey("conversations.conversation_id"),
        nullable=True,
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )
