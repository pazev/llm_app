from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from db.models.message import Message
from db.models.message_feedback import MessageFeedback


class FeedbackRepository:
    def __init__(self, session: Session):
        self._session = session

    def create(
        self,
        message_id: int,
        positive_feedback: Optional[bool] = None,
        comment: Optional[str] = None,
    ) -> MessageFeedback:
        feedback = MessageFeedback(
            message_id=message_id,
            positive_feedback=positive_feedback,
            comment=comment,
            datetime=datetime.now(timezone.utc),
        )
        self._session.add(feedback)
        self._session.flush()
        return feedback

    def list_by_message_ids(
        self, message_ids: List[int]
    ) -> List[MessageFeedback]:
        if not message_ids:
            return []
        return (
            self._session.query(MessageFeedback)
            .filter(
                MessageFeedback.message_id.in_(message_ids)
            )
            .all()
        )

    def count_by_conversation(
        self, conversation_id: int
    ) -> int:
        return (
            self._session.query(MessageFeedback)
            .join(
                Message,
                MessageFeedback.message_id == Message.message_id,
            )
            .filter(
                Message.conversation_id == conversation_id
            )
            .count()
        )
