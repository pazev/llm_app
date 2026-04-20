from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from db.models.message import Message


class MessageRepository:
    def __init__(self, session: Session):
        self._session = session

    def create(
        self,
        conversation_id: int,
        sender: str,
        content: str,
        message_context: Optional[List] = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            sender=sender,
            content=content,
            message_context=message_context,
            datetime=datetime.utcnow(),
        )
        self._session.add(message)
        self._session.flush()
        return message

    def get_by_id(self, message_id: int) -> Message:
        return self._session.get(Message, message_id)

    def list_by_conversation(
        self, conversation_id: int
    ) -> List[Message]:
        return (
            self._session.query(Message)
            .filter(
                Message.conversation_id == conversation_id
            )
            .order_by(Message.datetime.asc())
            .all()
        )

    def count_by_conversation(
        self, conversation_id: int
    ) -> int:
        return (
            self._session.query(Message)
            .filter(
                Message.conversation_id == conversation_id
            )
            .count()
        )

    def sum_tokens_by_conversation(
        self, conversation_id: int
    ) -> dict:
        messages = (
            self._session.query(Message)
            .filter(
                Message.conversation_id == conversation_id,
                Message.sender == "llm",
            )
            .all()
        )
        total = input_t = output_t = 0
        for msg in messages:
            for ctx in msg.message_context or []:
                total += ctx.get("token_usage", 0)
                input_t += ctx.get("input_tokens", 0)
                output_t += ctx.get("output_tokens", 0)
        return {
            "token_usage": total,
            "input_tokens": input_t,
            "output_tokens": output_t,
        }
