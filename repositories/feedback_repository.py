from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from db.models.message import Message
from db.models.message_feedback import MessageFeedback


class FeedbackRepository:
    def __init__(self, session: Session):
        self._session = session

    def upsert(
        self,
        message_id: int,
        positive_feedback: Optional[bool] = None,
        comment: Optional[str] = None,
    ) -> MessageFeedback:
        feedback = (
            self._session.query(MessageFeedback)
            .filter(MessageFeedback.message_id == message_id)
            .first()
        )
        if feedback is None:
            feedback = MessageFeedback(
                message_id=message_id,
                positive_feedback=positive_feedback,
                comment=comment,
                datetime=datetime.utcnow(),
            )
            self._session.add(feedback)
        else:
            if positive_feedback is not None:
                feedback.positive_feedback = positive_feedback
            if comment is not None:
                feedback.comment = comment
            feedback.datetime = datetime.utcnow()
        self._session.flush()
        return feedback

    def get_by_message(
        self, message_id: int
    ) -> MessageFeedback:
        return (
            self._session.query(MessageFeedback)
            .filter(MessageFeedback.message_id == message_id)
            .first()
        )

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
