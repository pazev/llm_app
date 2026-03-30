from abc import ABC, abstractmethod


class ChatService(ABC):
    @abstractmethod
    def get_response(self, user_message: str, conversation_history: list[dict]) -> str:
        """Return the LLM response for the given user message and conversation history.

        Args:
            user_message: The latest message from the user.
            conversation_history: List of prior messages as dicts with keys
                'role' ('user' or 'assistant') and 'content'.

        Returns:
            The LLM response as a string.
        """
