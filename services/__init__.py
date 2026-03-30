import os
from services.chat_service import ChatService


def get_llm_service() -> ChatService:
    service_name = os.environ.get("LLM_SERVICE", "stub")
    if service_name == "openai":
        from services.openai_service import OpenAILangChainService
        return OpenAILangChainService()
    from services.stub_llm_service import StubLLMService
    return StubLLMService()
