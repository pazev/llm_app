from services.chat_service import ChatService


class StubLLMService(ChatService):
    def get_response(self, user_message: str, conversation_history: list[dict]) -> str:
        return "Message Processed"
