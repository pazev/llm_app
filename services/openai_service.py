import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from services.chat_service import ChatService
from tools import ALL_TOOLS

DEFAULT_SYSTEM_PROMPT = (
    "You are a business advisor assistant for managers and directors. "
    "Provide clear, concise, and actionable business answers."
)


class OpenAILangChainService(ChatService):
    def __init__(self, system_prompt: str = DEFAULT_SYSTEM_PROMPT):
        self._system_prompt = system_prompt
        llm = ChatOpenAI(
            model="gpt-4o",
            api_key=os.environ["OPENAI_API_KEY"],
        )
        self._llm = llm.bind_tools(ALL_TOOLS) if ALL_TOOLS else llm
        self._tools_by_name: dict[str, BaseTool] = {t.name: t for t in ALL_TOOLS}

    def get_response(self, user_message: str, conversation_history: list[dict]) -> str:
        messages = [SystemMessage(content=self._system_prompt)]
        for entry in conversation_history:
            if entry["role"] == "user":
                messages.append(HumanMessage(content=entry["content"]))
            else:
                messages.append(AIMessage(content=entry["content"]))
        messages.append(HumanMessage(content=user_message))

        max_iterations = 10
        for _ in range(max_iterations):
            response = self._llm.invoke(messages)
            messages.append(response)

            if not response.tool_calls:
                return response.content

            for tool_call in response.tool_calls:
                tool = self._tools_by_name[tool_call["name"]]
                result = tool.invoke(tool_call["args"])
                messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))

        raise RuntimeError(f"Agent did not finish within {max_iterations} iterations.")
