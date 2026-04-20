from typing import Any, Dict

from langchain_core.messages import BaseMessage


def message_to_dict(
    message: BaseMessage,
) -> Dict[str, Any]:
    msg_type = type(message).__name__

    usage = getattr(message, "usage_metadata", None)
    input_tokens = (
        usage["input_tokens"] if usage else 0
    )
    output_tokens = (
        usage["output_tokens"] if usage else 0
    )
    token_usage = (
        usage["total_tokens"] if usage else 0
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
            getattr(message, "additional_kwargs", {})
            or {}
        ),
        "response_metadata": (
            getattr(message, "response_metadata", {})
            or {}
        ),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "token_usage": token_usage,
        "tool_calls": tool_calls,
    }
