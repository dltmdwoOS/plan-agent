from pydantic import BaseModel, Field
from typing   import Dict, Any, Optional

from agent.utils import load_locale_const
    
const = load_locale_const()
class Plan(BaseModel):
    """
    Model that structures a plan.

    Args:
        plan (List[Dict[str, Any]]): List of dictionaries representing the steps of the plan.
            Each dictionary includes 'tool' (the action to perform) and 'message' (additional notes).
    """
    
    plan: list[Dict[str, Any]] = Field(
        description=const.PLAN_MODEL_DESC['plan']
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
        description=const.TOOL_DECISION_MODEL_DESC['tool']
    )
    tool_input: Dict[str, Any] = Field(
        description=const.TOOL_DECISION_MODEL_DESC['tool_input']
    )
    message: Optional[str] = Field(
        default="",
        description=const.TOOL_DECISION_MODEL_DESC['message']
    )
    
class Validation(BaseModel):
    """
    Model that structures the validation result of the plan execution.

    Args:
        is_valid (bool): Whether the plan and execution were valid. True means the plan was executed successfully; False means it failed and a new plan is needed.
        message (str): Description message for the validation result. Optional, can provide additional information about the validation result.
    """
    
    is_valid: bool = Field(
        description=const.VALIDATION_MODEL_DESC['is_valid']
    )
    message: str = Field(
        default="",
        description=const.VALIDATION_MODEL_DESC['message']
    )
    
class Entities(BaseModel):
    """
    Model that structures entities.

    Args:
        entities (Dict[str, Any]): A dictionary representing eneities worth remembering.
    """
    
    entities: Dict[str, Any] = Field(
        description=const.ENTITIES_MODEL_DESC['entities']
    )
