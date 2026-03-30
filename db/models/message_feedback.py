from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from db.base import Base


class MessageFeedback(Base):
    __tablename__ = "message_feedback"

    message_feedback_id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.message_id"), nullable=False)
    positive_feedback = Column(Boolean, nullable=True)
    comment = Column(Text, nullable=True)
    datetime = Column(DateTime, default=datetime.utcnow, nullable=False)

    message = relationship("Message", back_populates="feedback")
