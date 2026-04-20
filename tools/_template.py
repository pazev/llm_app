"""
Tool template — copy this file to create a new tool,
e.g. tools/get_sales_summary.py

Steps:
  1. Copy this file and rename it (snake_case,
     matches the tool function name).
  2. Define the Pydantic input and output schemas.
  3. Implement the function body.
  4. Register the tool in tools/__init__.py:
       from tools.my_tool import my_tool
       ALL_TOOLS = [..., my_tool]
"""

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


# -------------------------------------------------------
# Input schema
# -------------------------------------------------------

class TemplateToolInputSchema(BaseModel):
    """Describes the parameters the LLM must supply
    when calling this tool."""

    param_one: str = Field(
        description="What this parameter represents."
    )
    param_two: int = Field(
        default=10,
        description="Optional parameter with a default.",
    )


# -------------------------------------------------------
# Output schema
# -------------------------------------------------------

class TemplateToolOutputSchema(BaseModel):
    """Describes the data returned by this tool."""

    result: str = Field(
        description="The output produced by the tool."
    )


# -------------------------------------------------------
# Tool definition
# -------------------------------------------------------

def _tool_description() -> str:
    return (
        "One-sentence description used by the LLM to"
        " decide when to call this tool. "
        "Add extra detail here if the decision logic"
        " is non-obvious. This string becomes the"
        " tool's `description` in the OpenAI spec."
    )


def _template_tool_fn(
    param_one: str,
    param_two: int = 10,
) -> TemplateToolOutputSchema:
    # TODO: implement tool logic
    raise NotImplementedError


template_tool = StructuredTool(
    name="template_tool",
    description=_tool_description(),
    args_schema=TemplateToolInputSchema,
    func=_template_tool_fn,
)
