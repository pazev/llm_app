import random
from typing import Any, Callable, Dict, List, Tuple

from langchain_core.messages import AIMessage
from langchain_core.messages.ai import UsageMetadata

from services._message_utils import message_to_dict
from services.chat_service import ChatService

_STUB_RESPONSE = "Message Processed"


class StubLLMService(ChatService):
    def __init__(self):
        self._system_prompt_maker: Callable[[], str] = (
            lambda: ""
        )

    def set_model(self, model: str) -> None:
        pass

    def set_system_prompt_maker(
        self, maker: Callable[[], str]
    ) -> None:
        self._system_prompt_maker = maker

    def get_system_prompt_maker(self) -> Callable[[], str]:
        return self._system_prompt_maker

    def get_response(
        self,
        user_message: str,
        conversation_history: List[Dict],
    ) -> Tuple[str, List[Dict[str, Any]]]:
        input_tokens = len(user_message.split())
        output_tokens = random.randint(10, 100)
        msg = AIMessage(
            content=_STUB_RESPONSE,
            usage_metadata=UsageMetadata(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
            ),
        )
        return _STUB_RESPONSE, [message_to_dict(msg)]
