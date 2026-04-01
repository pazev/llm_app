from typing import Any, Callable
from services.chat_service import ChatService


class StubLLMService(ChatService):
    def __init__(self):
        self._system_prompt_maker: Callable[[], str] = lambda: ""

    def set_system_prompt_maker(self, maker: Callable[[], str]) -> None:
        self._system_prompt_maker = maker

    def get_system_prompt_maker(self) -> Callable[[], str]:
        return self._system_prompt_maker

    def get_response(self, user_message: str, conversation_history: list[dict]) -> tuple[str, list[dict[str, Any]]]:
        return "Message Processed", []
