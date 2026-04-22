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
from services_llm.chat_service import ChatService
from services_llm.models import list_available_models


class ChatController:
    def __init__(self, chat_service: ChatService):
        self._chat_service = chat_service

    def list_available_models(self) -> List[str]:
        return list_available_models()

    def set_model(self, model: str) -> None:
        self._chat_service.set_model(model)

    def resume_conversation(
        self,
        conversation_id: int,
        user_id: Optional[int] = None,
    ) -> Tuple[ConversationResponse, List[MessageResponse]]:
        with get_db() as db:
            new_conv = ConversationRepository(db).create(
                title=f"Resumed from #{conversation_id}",
                resumed_from_conversation_id=conversation_id,
                user_id=user_id,
            )
            old_messages = MessageRepository(
                db
            ).list_by_conversation(conversation_id)
            msg_repo = MessageRepository(db)
            new_messages = [
                msg_repo.create(
                    conversation_id=new_conv.conversation_id,
                    sender=m.sender,
                    content=m.content,
                    message_context=m.message_context,
                )
                for m in old_messages
            ]
            old_ids = [m.message_id for m in old_messages]
            feedbacks = FeedbackRepository(
                db
            ).list_by_message_ids(old_ids)
            fb_by_old_id = {
                fb.message_id: fb for fb in feedbacks
            }
            id_map = {
                old.message_id: new.message_id
                for old, new in zip(old_messages, new_messages)
            }
            fb_repo = FeedbackRepository(db)
            for old_id, fb in fb_by_old_id.items():
                fb_repo.upsert(
                    message_id=id_map[old_id],
                    positive_feedback=fb.positive_feedback,
                    comment=fb.comment,
                )
            return (
                ConversationResponse.model_validate(new_conv),
                [
                    MessageResponse.model_validate(m)
                    for m in new_messages
                ],
            )

    def start_conversation(
        self,
        title: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> ConversationResponse:
        dto = ConversationCreate(title=title)
        with get_db() as db:
            conv = ConversationRepository(db).create(
                title=dto.title,
                user_id=user_id,
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

    def list_conversations(
        self, user_id: Optional[int] = None
    ) -> List[ConversationSummary]:
        with get_db() as db:
            conversations = (
                ConversationRepository(db).list_all(
                    user_id=user_id
                )
            )
            msg_repo = MessageRepository(db)
            fb_repo = FeedbackRepository(db)
            return [
                ConversationSummary(
                    conversation_id=conv.conversation_id,
                    datetime_start=conv.datetime_start,
                    title=conv.title,
                    resumed_from_conversation_id=(
                        conv.resumed_from_conversation_id
                    ),
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
                    username=(
                        conv.user.username
                        if conv.user
                        else None
                    ),
                    **msg_repo.sum_tokens_by_conversation(
                        conv.conversation_id
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
    ) -> Dict[int, List[FeedbackResponse]]:
        with get_db() as db:
            messages = MessageRepository(
                db
            ).list_by_conversation(conversation_id)
            message_ids = [m.message_id for m in messages]
            feedbacks = FeedbackRepository(
                db
            ).list_by_message_ids(message_ids)
            result: Dict[int, List[FeedbackResponse]] = {}
            for fb in feedbacks:
                r = FeedbackResponse.model_validate(fb)
                result.setdefault(fb.message_id, []).append(r)
            return result

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
            feedback = FeedbackRepository(db).create(
                message_id=dto.message_id,
                positive_feedback=dto.positive_feedback,
                comment=dto.comment,
            )
            return FeedbackResponse.model_validate(feedback)
