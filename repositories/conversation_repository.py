from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from db.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, session: Session):
        self._session = session

    def create(
        self,
        title: Optional[str] = None,
        resumed_from_conversation_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> Conversation:
        conversation = Conversation(
            datetime_start=datetime.utcnow(),
            title=title,
            resumed_from_conversation_id=(
                resumed_from_conversation_id
            ),
            user_id=user_id,
        )
        self._session.add(conversation)
        self._session.flush()
        return conversation

    def get_by_id(
        self, conversation_id: int
    ) -> Conversation:
        return self._session.get(Conversation, conversation_id)

    def list_all(self) -> List[Conversation]:
        return (
            self._session.query(Conversation)
            .order_by(Conversation.datetime_start.desc())
            .all()
        )
