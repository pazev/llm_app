import os
from typing import Callable, Optional
from services.chat_service import ChatService


def get_llm_service(
    system_prompt_maker: Optional[Callable[[], str]] = None,
) -> ChatService:
    service_name = os.environ.get("LLM_SERVICE", "stub")
    if service_name == "openai":
        from services.openai_service import (
            OpenAILangChainService,
        )
        service = OpenAILangChainService()
    else:
        from services.stub_llm_service import StubLLMService
        service = StubLLMService()
    if system_prompt_maker is not None:
        service.set_system_prompt_maker(system_prompt_maker)
        return service
    raise ValueError(
        "system_prompt_maker is required."
    )
