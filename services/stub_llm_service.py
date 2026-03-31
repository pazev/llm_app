from typing import Any
from services.chat_service import ChatService


class StubLLMService(ChatService):
    def get_response(self, user_message: str, conversation_history: list[dict]) -> tuple[str, list[dict[str, Any]]]:
        return "Message Processed", []
