from abc import ABC, abstractmethod
from typing import Any, Callable


class ChatService(ABC):
    @abstractmethod
    def set_system_prompt_maker(self, maker: Callable[[], str]) -> None:
        """Set the callable used to produce the system prompt at request time."""

    @abstractmethod
    def get_system_prompt_maker(self) -> Callable[[], str]:
        """Return the current system prompt maker callable."""

    @abstractmethod
    def get_response(self, user_message: str, conversation_history: list[dict]) -> tuple[str, list[dict[str, Any]]]:
        """Return the LLM response and the full message context for the interaction.

        Args:
            user_message: The latest message from the user.
            conversation_history: List of prior messages as dicts with keys
                'role' ('user' or 'assistant') and 'content'.

        Returns:
            A tuple of (final_answer, context) where context is a list of message
            dicts produced during the agent loop (AI responses and tool results),
            each with keys: type, content, additional_kwargs, response_metadata,
            token_usage, tool_calls.
        """
