"""
Tool registry — import every tool here and add it to ALL_TOOLS.

The service layer binds this list to the LLM via
llm.bind_tools(ALL_TOOLS).
"""
from typing import List

# from tools.my_tool import my_tool

ALL_TOOLS: List = []
