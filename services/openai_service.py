import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from services.chat_service import ChatService

SYSTEM_PROMPT = (
    "You are a business advisor assistant for managers and directors. "
    "Provide clear, concise, and actionable business answers."
)


class OpenAILangChainService(ChatService):
    def __init__(self):
        self._llm = ChatOpenAI(
            model="gpt-4o",
            api_key=os.environ["OPENAI_API_KEY"],
        )

    def get_response(self, user_message: str, conversation_history: list[dict]) -> str:
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        for entry in conversation_history:
            if entry["role"] == "user":
                messages.append(HumanMessage(content=entry["content"]))
            else:
                messages.append(AIMessage(content=entry["content"]))
        messages.append(HumanMessage(content=user_message))

        response = self._llm.invoke(messages)
        return response.content
