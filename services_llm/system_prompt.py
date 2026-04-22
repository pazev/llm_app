from typing import Callable


def system_prompt_maker() -> str:
    return ""


def get_system_prompt_maker() -> Callable[[], str]:
    return system_prompt_maker
