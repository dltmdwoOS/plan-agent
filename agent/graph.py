from dotenv import load_dotenv
import yaml

from agent.memory.memory import Memory
from agent.path import DESC_DIR
load_dotenv()
from langchain_core.messages import (
    HumanMessage,
    AIMessage
)

from agent.tool_registry import common_tool_registry as TOOL_REGISTRY, special_tool_registry as SPECIAL_TOOL_REGISTRY
from agent.chains import PlanChain, ToolChain, ValidationChain, ResponseChain
from agent.utils import save_chat_memory, load_chat_memory

class Agent:
    def __init__(self, session_id, recursion_limit=5, max_memory_tokens=1e4):
        self.session_id = session_id
        self.recursion_limit = recursion_limit
        self.memory = Memory(max_memory_tokens)
        self.chains = [] # Name of chains used in this agent, for debugging purposes
        
    def chat(self, user_input: str, debug=False):
        raise NotImplementedError("This method should be implemented in subclasses.")
     
class PlanAgent(Agent):
    def __init__(self, session_id, recursion_limit=5, max_memory_tokens=1e4, is_stream: bool=True):
        super().__init__(session_id, recursion_limit, max_memory_tokens)
        
        self.tools = TOOL_REGISTRY.values()
        self.special_tools = SPECIAL_TOOL_REGISTRY
        self.plan_chain = PlanChain()
        self.tool_chain = ToolChain()
        self.validation_chain = ValidationChain()
        self.response_chain = ResponseChain(is_stream=is_stream)

        self.chains = [
            self.plan_chain.name,
            self.tool_chain.name,
            self.validation_chain.name,
            self.response_chain.name
        ]

        self.save_request = False

    def _add_buffer(self, buf: list, string: str, debug: bool=False):
        buf.append(string)
        if debug:
            print(string)
    
    def _tool_validator(self, tool_json: dict) -> tuple[str, str]:
        """
        Validate the provided tool_json dictionary.

        This function checks that the dictionary contains the required keys "tool" and "message"
        and does not contain any unexpected keys (allowed keys are "tool", "message", and optionally "tool_input").
        Additionally, if the "tool_input" key is present, the function loads the corresponding
        YAML description from the descriptions directory (using the tool name) and compares its "args" key
        with the value of "tool_input". If they match exactly, it returns ("jump", "").

        Args:
            tool_json (dict): The dictionary to validate.

        Returns:
            tuple[str, str]:
                - "true" and an empty message if validation passes without "tool_input" check,
                - "jump" and an empty message if "tool_input" is present and exactly matches the description's args,
                - "false" and an error message if any validation errors occur.
        """
        allowed_keys = {"tool", "message", "tool_input"}
        required_keys = {"tool", "message"}
        
        json_keys = set(tool_json.keys())
        
        # Check for unexpected keys.
        unexpected_keys = json_keys - allowed_keys
        if unexpected_keys:
            return ("false", f"Unexpected keys present: {unexpected_keys}. Allowed keys are {allowed_keys}.")
        
        # Check for missing required keys.
        missing_keys = required_keys - json_keys
        if missing_keys:
            return ("false", f"Missing required keys: {missing_keys}.")
        
        # If 'tool_input' exists, try to perform YAML args comparison.
        if "tool_input" in tool_json:
            tool_name = tool_json["tool"]
            yaml_path = DESC_DIR / f"{tool_name}.yaml"
            if not yaml_path.exists():
                return ("false", f"Description file not found for tool: {tool_name}.")
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    desc_yaml = yaml.safe_load(f)
            except Exception as e:
                return ("false", f"Failed to load YAML for tool {tool_name}: {e}")
            
            # Get the 'args' section from the YAML.
            expected_args = desc_yaml.get("args")
            provided_args = tool_json["tool_input"]
            if provided_args == expected_args:
                return ("jump", "")
        
        # Validation passed.
        return ("true", "")
    
    def _tool_use(self, tool: str, tool_input: dict):
        for tool_candidate in self.tools:
            if tool_candidate.name == tool:
                tool_output = tool_candidate.invoke(tool_input)
                return tool_output
        return None

    def _special_tool_use(self, tool_name: str, tool_message: str):
        if tool_name == "thought":
            tool_output = tool_message
            return tool_output
        elif tool_name == "save_chat_memory":
            self.save_request = True
            return "Conversation history has been saved successfully."
        elif tool_name == "clear_chat_memory":
            self.memory.clear_memory()
            return "Conversation history has been reset successfully."
        return None

    def _response(self, buffer):
        """Get response as string type, and simultaneously print it."""
        input = [HumanMessage(content="\n".join(buffer))]
        response = self.response_chain.invoke({"memory": self.memory.memory, "input": input})

        if type(response) == str:
            print(f"Response:\n{response}")

        else:
            response_buffer = []

            print("Response:")
            for token in response:
                print(token, end="", flush=True)
                response_buffer.append(token)
                
            response = "".join(response_buffer)
        
        return response
    
    def chat(self, user_input: str, is_debug=False):
        _buffer = []
        _input = []
        
        recursion = 0
        accepted = False
        
        self._add_buffer(_buffer, f"Input: {user_input}", is_debug)
        while recursion < self.recursion_limit and not accepted:
            self._add_buffer(_buffer, f"\nAttempt {recursion+1}", is_debug)
            
            # Planning Step
            _input = [HumanMessage(content="\n".join(_buffer))]
            plan = self.plan_chain.invoke({"memory": self.memory.memory, "input": _input}).plan
            self._add_buffer(_buffer, f"Plan: {plan}", is_debug)

            # Tool Step
            if not plan:
                raise ValueError("Plan is empty. Cannot proceed to validation.")
            
            for step, tool_json in enumerate(plan):
                ## 0. Incomplete tool validation
                validation, message = self._tool_validator(tool_json)
                if validation=='false':
                    self._add_buffer(_buffer, f"Step {step+1} Error : {message}", is_debug)
                    break # To validation step
                
                tool_name, tool_message = tool_json['tool'], tool_json['message']
                tool_output = None

                # ---------------------------- Special tool : do not need any tool input ----------------------------
                tool_output = self._special_tool_use(tool_name, tool_message)
                if tool_output:
                    self._add_buffer(_buffer, f"Step {step+1} Output: {tool_output}", is_debug)
                    continue

                # ----------------------------   Common tool : do need some tool inputs   ----------------------------
                elif validation=='true':
                    ## 1. Complete the current step
                    self._add_buffer(_buffer, f"Current Step: {tool_json} TODO!")
                    _input = [HumanMessage(content="\n".join(_buffer))]
                    tool_json = self.tool_chain.invoke(tool=tool_name, vars={"memory": self.memory.memory, "input": _input})
                    _buffer.pop()  # Remove the last incomplete tool from the buffer
                elif validation=='jump':
                    pass
                
                ## 2. Find the tool in the available tools and invoke it
                self._add_buffer(_buffer, f"Plan Step {step+1} Tool: {tool_json}", is_debug)
                
                tool, tool_input = tool_json.tool, tool_json.tool_input
                tool_output = self._tool_use(tool, tool_input)
                if tool_output:
                    self._add_buffer(
                        _buffer, 
                        (
                            f"Plan Step {step+1} Tool Output:\n"
                            f"<OUTPUT START>\n{tool_output}\n<OUTPUT END>"
                        ),
                        is_debug
                    )
                    continue

                if tool_output is None:
                    raise ValueError(f"Tool '{tool}' not found in available tools.")

            # Validation Step
            _input = [HumanMessage(content="\n".join(_buffer))]
            validation = self.validation_chain.invoke({"input": _input})
            if validation.is_valid:
                self._add_buffer(
                    _buffer,
                    (
                        "Accepted: True\n"
                        f"Validation Message: {validation.message}"
                    ),
                    is_debug
                )
                accepted = True
            else:
                self._add_buffer(
                    _buffer, 
                    (
                        "Accepted: False\n"
                        f"Validation Message: {validation.message}\n"
                        "The above process did not pass validation. You need to re-plan based on the validation result."
                    ),
                    is_debug
                )
                recursion += 1
        
        # Response Step
        if not accepted:
            self._add_buffer(_buffer, "Maximum number of attempts exceeded. Further plan resets and tool usage are not possible.", is_debug)
            
        response = self._response(_buffer)
        self.memory.extend([HumanMessage(content="\n".join(_buffer)), AIMessage(content=response)])

        # If save requirement from `save_chat_memory`
        if self.save_request:
            self.memory.save_memory()
            self.save_request = False
        return response