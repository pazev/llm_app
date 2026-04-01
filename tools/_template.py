"""
Tool template — copy this file to create a new tool,
e.g. tools/get_sales_summary.py

Steps:
  1. Copy this file and rename it (snake_case, matches the
     tool function name).
  2. Define the Pydantic input schema (MyToolInput).
  3. Implement the function body.
  4. Register the tool in tools/__init__.py:
       from tools.my_tool import my_tool
       ALL_TOOLS = [..., my_tool]
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Input schema
# ---------------------------------------------------------------------------

class TemplateToolInput(BaseModel):
    """Describes the parameters the LLM must supply when
    calling this tool."""

    param_one: str = Field(
        description="What this parameter represents."
    )
    param_two: int = Field(
        default=10,
        description="Optional parameter with a default.",
    )


# ---------------------------------------------------------------------------
# Tool definition
# ---------------------------------------------------------------------------

@tool(args_schema=TemplateToolInput)
def template_tool(
    param_one: str, param_two: int = 10
) -> str:
    """One-sentence description used by the LLM to decide
    when to call this tool.

    Add extra detail here if the decision logic is
    non-obvious. This docstring becomes the tool's
    `description` in the OpenAI function spec.
    """
    # TODO: implement tool logic
    raise NotImplementedError
