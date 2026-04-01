from typing import Dict, List, Optional, Tuple
from db.session import get_db
from repositories.conversation_repository import (
    ConversationRepository,
)
from repositories.message_repository import MessageRepository
from repositories.feedback_repository import FeedbackRepository
from schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationSummary,
    MessageCreate,
    MessageResponse,
    SenderEnum,
    FeedbackSubmit,
    FeedbackResponse,
)
from services.chat_service import ChatService
from services.models import list_available_models


class ChatController:
    def __init__(self, chat_service: ChatService):
        self._chat_service = chat_service

    def list_available_models(self) -> List[str]:
        return list_available_models()

    def set_model(self, model: str) -> None:
        self._chat_service.set_model(model)

    def resume_conversation(
        self, conversation_id: int
    ) -> Tuple[ConversationResponse, List[MessageResponse]]:
        messages = self.get_conversation_messages(
            conversation_id
        )
        new_conv = self.start_conversation(
            title=f"Resumed from #{conversation_id}"
        )
        return new_conv, messages

    def start_conversation(
        self, title: Optional[str] = None
    ) -> ConversationResponse:
        dto = ConversationCreate(title=title)
        with get_db() as db:
            conv = ConversationRepository(db).create(
                title=dto.title
            )
            return ConversationResponse.model_validate(conv)

    def send_message(
        self,
        conversation_id: int,
        user_content: str,
        conversation_history: List[Dict],
    ) -> Tuple[MessageResponse, MessageResponse]:
        user_dto = MessageCreate(
            conversation_id=conversation_id,
            sender=SenderEnum.user,
            content=user_content,
        )

        llm_text, context = self._chat_service.get_response(
            user_dto.content, conversation_history
        )

        llm_dto = MessageCreate(
            conversation_id=conversation_id,
            sender=SenderEnum.llm,
            content=llm_text,
            message_context=context or None,
        )

        with get_db() as db:
            msg_repo = MessageRepository(db)
            user_msg = msg_repo.create(
                conversation_id=user_dto.conversation_id,
                sender=user_dto.sender.value,
                content=user_dto.content,
            )
            user_response = MessageResponse.model_validate(
                user_msg
            )
            llm_msg = msg_repo.create(
                conversation_id=llm_dto.conversation_id,
                sender=llm_dto.sender.value,
                content=llm_dto.content,
                message_context=llm_dto.message_context,
            )
            llm_response = MessageResponse.model_validate(
                llm_msg
            )

        return user_response, llm_response

    def list_conversations(self) -> List[ConversationSummary]:
        with get_db() as db:
            conversations = (
                ConversationRepository(db).list_all()
            )
            msg_repo = MessageRepository(db)
            fb_repo = FeedbackRepository(db)
            return [
                ConversationSummary(
                    conversation_id=conv.conversation_id,
                    datetime_start=conv.datetime_start,
                    title=conv.title,
                    message_count=(
                        msg_repo.count_by_conversation(
                            conv.conversation_id
                        )
                    ),
                    feedback_count=(
                        fb_repo.count_by_conversation(
                            conv.conversation_id
                        )
                    ),
                )
                for conv in conversations
            ]

    def get_conversation_messages(
        self, conversation_id: int
    ) -> List[MessageResponse]:
        with get_db() as db:
            messages = MessageRepository(
                db
            ).list_by_conversation(conversation_id)
            return [
                MessageResponse.model_validate(m)
                for m in messages
            ]

    def get_conversation_feedbacks(
        self, conversation_id: int
    ) -> Dict[int, FeedbackResponse]:
        with get_db() as db:
            messages = MessageRepository(
                db
            ).list_by_conversation(conversation_id)
            message_ids = [m.message_id for m in messages]
            feedbacks = FeedbackRepository(
                db
            ).list_by_message_ids(message_ids)
            return {
                fb.message_id: FeedbackResponse.model_validate(
                    fb
                )
                for fb in feedbacks
            }

    def submit_feedback(
        self,
        message_id: int,
        positive_feedback: bool,
        comment: str,
    ) -> FeedbackResponse:
        dto = FeedbackSubmit(
            message_id=message_id,
            positive_feedback=positive_feedback,
            comment=comment,
        )
        with get_db() as db:
            feedback = FeedbackRepository(db).upsert(
                message_id=dto.message_id,
                positive_feedback=dto.positive_feedback,
                comment=dto.comment,
            )
            return FeedbackResponse.model_validate(feedback)
