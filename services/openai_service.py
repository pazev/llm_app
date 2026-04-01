import os
from typing import Any, Callable, Dict, List, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
    BaseMessage,
)
from langchain_core.tools import BaseTool
from services.chat_service import ChatService
from tools import ALL_TOOLS

DEFAULT_SYSTEM_PROMPT = (
    "You are a business advisor assistant for managers and "
    "directors. Provide clear, concise, and actionable "
    "business answers."
)


class OpenAILangChainService(ChatService):
    def __init__(
        self,
        system_prompt_maker: Callable[[], str] = (
            lambda: DEFAULT_SYSTEM_PROMPT
        ),
        **kwargs,
    ):
        self._system_prompt_maker = system_prompt_maker
        llm = ChatOpenAI(
            model=os.environ.get("DEFAULT_MODEL", "gpt-4o"),
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.environ.get("OPENAI_BASE_URL") or None,
            **kwargs,
        )
        self._llm = (
            llm.bind_tools(ALL_TOOLS) if ALL_TOOLS else llm
        )
        self._tools_by_name: Dict[str, BaseTool] = {
            t.name: t for t in ALL_TOOLS
        }

    def _message_to_dict(
        self, message: BaseMessage
    ) -> Dict[str, Any]:
        msg_type = type(message).__name__
        token_usage = 0
        if msg_type == "AIMessage":
            token_usage = (
                (
                    getattr(message, "response_metadata", None)
                    or {}
                )
                .get("token_usage", {})
                .get("total_tokens", 0)
            )
        tool_calls = [
            {
                "name": tc["name"],
                "args": tc["args"],
                "type": tc["type"],
            }
            for tc in (
                getattr(message, "tool_calls", None) or []
            )
        ]
        return {
            "type": msg_type,
            "content": (
                message.content
                if isinstance(message.content, str)
                else str(message.content)
            ),
            "additional_kwargs": (
                getattr(message, "additional_kwargs", {}) or {}
            ),
            "response_metadata": (
                getattr(message, "response_metadata", {}) or {}
            ),
            "token_usage": token_usage,
            "tool_calls": tool_calls,
        }

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
        messages: List[BaseMessage] = [
            SystemMessage(content=self._system_prompt_maker())
        ]
        for entry in conversation_history:
            if entry["role"] == "user":
                messages.append(
                    HumanMessage(content=entry["content"])
                )
            else:
                messages.append(
                    AIMessage(content=entry["content"])
                )
        messages.append(HumanMessage(content=user_message))

        context: List[Dict[str, Any]] = []
        max_iterations = 10
        for _ in range(max_iterations):
            response = self._llm.invoke(messages)
            messages.append(response)
            context.append(self._message_to_dict(response))

            if not response.tool_calls:
                return response.content, context

            for tool_call in response.tool_calls:
                tool = self._tools_by_name[tool_call["name"]]
                result = tool.invoke(tool_call["args"])
                tool_msg = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                )
                messages.append(tool_msg)
                context.append(self._message_to_dict(tool_msg))

        raise RuntimeError(
            f"Agent did not finish within "
            f"{max_iterations} iterations."
        )
