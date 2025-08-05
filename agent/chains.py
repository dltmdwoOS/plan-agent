
from pydantic import ValidationError
from langchain_core.output_parsers import StrOutputParser

from agent.model.chain_config import ChainConfig
from agent.model.model import Entities, Plan, ToolDecision, Validation
from agent.llm import get_llm
from agent.utils import build_prompt, load_tool_descs, tool_desc_format
from agent.path import PROMPT_DIR

CHAINS = {
    c.name: c for c in [
        ChainConfig("PlanChain",        PROMPT_DIR / "plan.yaml"),
        ChainConfig("ToolChain",        PROMPT_DIR / "tool.yaml"),
        ChainConfig("ValidationChain",  PROMPT_DIR / "validation.yaml"),
        ChainConfig("ResponseChain",    PROMPT_DIR / "response.yaml"),
        ChainConfig("VisionChain",      PROMPT_DIR / "vision.yaml"),
        ChainConfig("SummaryChain",     PROMPT_DIR / "summary.yaml"),
    ]
}

# Tool Description
_tool_desc = load_tool_descs()

COMMON_TOOL_DESC_LIST   = [d for d in _tool_desc if d["kind"] == "common"]
SPECIAL_TOOL_DESC_LIST  = [d for d in _tool_desc if d["kind"] == "special"]
COMMON_TOOL_DESC        = "\n\n\n".join(tool_desc_format(d) for d in COMMON_TOOL_DESC_LIST)
SPECIAL_TOOL_DESC       = "\n\n\n".join(tool_desc_format(d) for d in SPECIAL_TOOL_DESC_LIST)
CURRENT_TOOL_DESC = lambda x: "".join(
    tool_desc_format(t)
    for t in COMMON_TOOL_DESC_LIST if t['name'] == x
)

class BaseChain():
    def __init__(self, name: str):
        self.name = name
        self.description = (
            "BaseChain is the base class for all chains. "
            "Inherit from this class to implement concrete chains."
        )
        self.llm = None
        self.system_messge = []
        self.few_shot = []
        self.prompt = None
        self.chain = None

    def invoke(self, vars: dict):
        """
        Execute the chain with the given memory and return the result.

        Args:
            vars: Variable dictionary required to invoke the chain.

        Returns:
            The result produced by the chain.
        """
        if self.chain is None:
            raise NotImplementedError("Chain is not implemented.")
        return self.chain.invoke(vars)

class PlanChain(BaseChain):
    def __init__(self, name: str = "PlanChain"):
        self.name = name
        self.description = (
            "PlanChain is responsible for creating an appropriate plan for the user's question. "
            "Based on the conversation history, it plans the next actions required to answer the current user query."
        )
        self.llm = get_llm(
            CHAINS[self.name],
            tags=["Plan"],
            temperature=0.3
        ).with_structured_output(Plan, method='function_calling')
        
        self.prompt = build_prompt(
            CHAINS[self.name],
            {'COMMON_TOOL_DESC': COMMON_TOOL_DESC, 'SPECIAL_TOOL_DESC': SPECIAL_TOOL_DESC},
            ["memory", "input"]
        )
        
        self.chain = self.prompt | self.llm

class ToolChain(BaseChain):
    def __init__(self, name: str = "ToolChain", max_attempt=3):
        self.name = name
        self.description = (
            "ToolChain selects and executes the appropriate tool for the current step "
            "according to the previously created plan in order to answer the user's question."
        )
        self.max_attempt = max_attempt
        self.llm = get_llm(
            CHAINS[self.name],
            tags=["Tool"]
        ).with_structured_output(ToolDecision, method='function_calling')
        self.prompt = None
        self.chain = None

    def invoke(self, tool: str, vars):
        self.prompt = build_prompt(
            CHAINS[self.name],
            {'TOOL_FOR_CURRENT_STEP': CURRENT_TOOL_DESC(tool)},
            ["memory", "input"]
        )
        self.chain = (self.prompt | self.llm).with_retry(
            retry_if_exception_type=(ValidationError, ValueError),
            stop_after_attempt=self.max_attempt,
            wait_exponential_jitter=True
        )
        return self.chain.invoke(vars)

class ValidationChain(BaseChain):
    def __init__(self, name: str = "ValidationChain"):
        self.name = name
        self.description = (
            "ValidationChain verifies whether the plan associated with the user's question has been executed correctly. "
            "It checks whether the plan proceeded as intended and whether meaningful results were produced. "
            "If the plan was not executed or the results are meaningless, it prompts the system to create a new plan."
        )
        self.llm = get_llm(
            CHAINS[self.name],
            tags=["Validation"]
        ).with_structured_output(Validation)
        self.prompt = build_prompt(
            CHAINS[self.name],
            extra_placeholders=["input"]
        )
        self.chain = self.prompt | self.llm

class ResponseChain(BaseChain):
    def __init__(self, name: str = "ResponseChain", is_stream: bool = True):
        self.name = name
        self.description = (
            "ResponseChain generates the final answer to the user's question. "
            "Using the information and reasoning gathered in previous steps, "
            "it produces a clear and friendly response."
        )
        self.llm = get_llm(
            CHAINS[self.name],
            tags=["Response"],
            temperature=0.3,
            streaming=is_stream
        )
        self.prompt = build_prompt(
            CHAINS[self.name],
            {'COMMON_TOOL_DESC': COMMON_TOOL_DESC, 'SPECIAL_TOOL_DESC': SPECIAL_TOOL_DESC},
            ["memory", "input"]
        )
        self.chain = self.prompt | self.llm | StrOutputParser()
        self.is_stream = is_stream

    def invoke(self, vars: dict):
        """
        Execute the chain with the given memory and return the result.

        Args:
            vars: Variable dictionary required to invoke the chain.

        Returns:
            The result produced by the chain.
        """
        if self.chain is None:
            raise NotImplementedError("Chain is not implemented.")

        if self.is_stream:
            return self.chain.stream(vars)
        else:
            return self.chain.invoke(vars)

class VisionChain(BaseChain):
    def __init__(self, name: str = "VisionChain"):
        self.name = name
        self.description = (
            "VisionChain creates friendly and clear answers "
            "by understanding user-provided images and text questions together."
        )
        self.llm = get_llm(
            CHAINS[self.name],
            tags=["Vision"],
            temperature=0.3
        )
        self.prompt = build_prompt(
            CHAINS[self.name],
            extra_placeholders=["memory", "input"]
        )
        self.chain = self.prompt | self.llm | StrOutputParser()
        
class SummaryChain(BaseChain):
    def __init__(self, name: str = "SummaryChain"):
        self.name = name
        self.description = (
            
        )
        self.llm = get_llm(
            CHAINS[self.name],
            tags=["Summary"],
            temperature=0.3
        )
        self.prompt = build_prompt(
            CHAINS[self.name],
            extra_placeholders=["memory", "input"]
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

class EntityMemoryChain(BaseChain):
    def __init__(self, name: str = "EntityMemoryChain"):
        self.name = name
        self.description = (
            
        )
        self.llm = get_llm(
            CHAINS[self.name],
            tags=["EntityMemory"],
            temperature=0.3
        ).with_structured_output(Entities, method='function_calling')
        self.prompt = build_prompt(
            CHAINS[self.name],
            extra_placeholders=["memory", "input"]
        )
        self.chain = self.prompt | self.llm