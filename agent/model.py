from dataclasses import dataclass
from pathlib import Path
from pydantic import BaseModel, Field
from typing   import Dict, Any, Optional

@dataclass
class ChainConfig:
    name: str
    yaml: Path
    model_family: str = "openai"
    model_name: str  = "gpt-4o-mini"
    
class Plan(BaseModel):
    """
    Model that structures a plan.

    Args:
        plan (List[Dict[str, Any]]): List of dictionaries representing the steps of the plan.
            Each dictionary includes 'tool' (the action to perform) and 'message' (additional notes).
    """
    
    plan: list[Dict[str, Any]] = Field(
        description=(
            "List of dictionaries representing the steps of the plan.\n"
            "Each dictionary includes 'tool' (the action to perform) and 'message' (additional notes).\n"
            "Example: [{'tool': 'get_datetime', 'message': 'Check today's date'}, {'tool': 'web_search', 'message': 'Using the date found in the previous step, search for today's weather in Seoul with a query like 'Month Day Seoul weather'}]\n"
        )
    )

class ToolDecision(BaseModel):
    """
    Model that structures the selected tool and its parameters.

    Args:
        tool (str): Name of the tool (must be one of the currently available tools)
        tool_input (Dict[str, Any]): Parameters as key-value pairs
        message (Optional[str]): Reason for selection or additional notes (optional)
    """
    tool: str = Field(
        description=f"Name of the tool to select. Must be one of the currently available tools."
    )
    tool_input: Dict[str, Any] = Field(
        description="Dictionary of parameters to pass when calling the selected tool."
    )
    message: Optional[str] = Field(
        default="",
        description="Reason for selection or notes (optional)"
    )
    
class Validation(BaseModel):
    """
    Model that structures the validation result of the plan execution.

    Args:
        is_valid (bool): Whether the plan and execution were valid. True means the plan was executed successfully; False means it failed and a new plan is needed.
        message (str): Description message for the validation result. Optional, can provide additional information about the validation result.
    """
    
    is_valid: bool = Field(
        description="Whether the plan and execution were valid. True means the plan was executed successfully; False means it failed and a new plan is needed."
    )
    message: str = Field(
        default="",
        description="Description message for the validation result. Optional, can provide additional information about the validation result."
    )
    
class EntityMemory(BaseModel):
    pass
