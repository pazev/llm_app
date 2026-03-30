from db.session import get_db
from repositories.conversation_repository import ConversationRepository
from repositories.message_repository import MessageRepository
from repositories.feedback_repository import FeedbackRepository
from schemas import (
    ConversationCreate, ConversationResponse,
    MessageCreate, MessageResponse, SenderEnum,
    FeedbackSubmit, FeedbackResponse,
)
from services.chat_service import ChatService


class ChatController:
    def __init__(self, chat_service: ChatService):
        self._chat_service = chat_service

    def start_conversation(self, title: str = None) -> ConversationResponse:
        dto = ConversationCreate(title=title)
        with get_db() as db:
            conv = ConversationRepository(db).create(title=dto.title)
            return ConversationResponse.model_validate(conv)

    def send_message(
        self, conversation_id: int, user_content: str, conversation_history: list[dict]
    ) -> tuple[MessageResponse, MessageResponse]:
        user_dto = MessageCreate(conversation_id=conversation_id, sender=SenderEnum.user, content=user_content)

        llm_text = self._chat_service.get_response(user_dto.content, conversation_history)

        llm_dto = MessageCreate(conversation_id=conversation_id, sender=SenderEnum.llm, content=llm_text)

        with get_db() as db:
            msg_repo = MessageRepository(db)
            user_msg = msg_repo.create(
                conversation_id=user_dto.conversation_id,
                sender=user_dto.sender.value,
                content=user_dto.content,
            )
            user_response = MessageResponse.model_validate(user_msg)
            llm_msg = msg_repo.create(
                conversation_id=llm_dto.conversation_id,
                sender=llm_dto.sender.value,
                content=llm_dto.content,
            )
            llm_response = MessageResponse.model_validate(llm_msg)

        return user_response, llm_response

    def submit_feedback(
        self,
        message_id: int,
        positive_feedback: bool,
        comment: str,
    ) -> FeedbackResponse:
        dto = FeedbackSubmit(message_id=message_id, positive_feedback=positive_feedback, comment=comment)
        with get_db() as db:
            feedback = FeedbackRepository(db).upsert(
                message_id=dto.message_id,
                positive_feedback=dto.positive_feedback,
                comment=dto.comment,
            )
            return FeedbackResponse.model_validate(feedback)
