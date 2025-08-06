from dotenv import load_dotenv
load_dotenv()

import yaml

from agent.memory import EntityMemory, Memory
from agent.path import DESC_DIR

from langchain_core.messages import (
    HumanMessage,
    AIMessage
)

from agent.tool_registry import common_tool_registry as TOOL_REGISTRY, special_tool_registry as SPECIAL_TOOL_REGISTRY
from agent.chains import PlanChain, ToolChain, ValidationChain, ResponseChain
from agent.utils import load_locale_const
const = load_locale_const()
TOOL_VALIDATOR_MSG  = const.TOOL_VALIDATOR_MSG
SPECIAL_TOOL_MSG    = const.SPECIAL_TOOL_MSG
CHAT_MSG            = const.CHAT_MSG

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
        self.entity_memory = EntityMemory()

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
            return ("false", TOOL_VALIDATOR_MSG['unexpected_keys'].format(unexpected_keys=unexpected_keys, allowed_keys=allowed_keys))
        
        # Check for missing required keys.
        missing_keys = required_keys - json_keys
        if missing_keys:
            return ("false", TOOL_VALIDATOR_MSG['missing_keys'].format(missing_keys=missing_keys))
        
        # If 'tool_input' exists, try to perform YAML args comparison.
        if "tool_input" in tool_json:
            tool_name = tool_json["tool"]
            yaml_path = DESC_DIR / f"{tool_name}.yaml"
            if not yaml_path.exists():
                return ("false", TOOL_VALIDATOR_MSG['yaml_path_not_exist'].format(tool_name=tool_name))
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    desc_yaml = yaml.safe_load(f)
            except Exception as e:
                return ("false", TOOL_VALIDATOR_MSG['yaml_load_error'].format(tool_name=tool_name, e=e))
            
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
            return SPECIAL_TOOL_MSG['save_chat_memory']
        elif tool_name == "clear_chat_memory":
            self.memory.clear_memory()
            return SPECIAL_TOOL_MSG['clear_chat_memory']
        return None
    
    # Planning step: generate a plan from the current buffer
    def _planning_step(self, buffer, is_debug):
        _input = [HumanMessage(content="\n".join(buffer))]
        plan = self.plan_chain.invoke({"memory": self.memory.memory, "input": _input}).plan
        self._add_buffer(buffer, CHAT_MSG['plan_message'].format(plan=plan), is_debug)
        return plan

    # Tool step: validate and execute each tool in the plan
    def _tool_step(self, buffer, plan, is_debug):
        if not plan:
            raise ValueError("Plan is empty. Cannot proceed to validation.")
        for step, tool_json in enumerate(plan):
            validation, message = self._tool_validator(tool_json)
            if validation=='false':
                self._add_buffer(buffer, CHAT_MSG['tool_validation_false_message'].format(step=step+1, message=message), is_debug)
                break
            tool_name, tool_message = tool_json['tool'], tool_json['message']
            tool_output = None
            # Special tool: no input required
            tool_output = self._special_tool_use(tool_name, tool_message)
            if tool_output:
                self._add_buffer(buffer, CHAT_MSG['tool_output_message'].format(step=step+1, tool_output=tool_output), is_debug)
                continue
            # Common tool: input required
            elif validation=='true':
                self._add_buffer(buffer, CHAT_MSG['current_tool_message'].format(tool_json=tool_json, entity_memory=self.entity_memory.entity_memory))
                _input = [HumanMessage(content="\n".join(buffer))]
                tool_json = self.tool_chain.invoke(tool=tool_name, vars={"input": _input})
                buffer.pop()
            self._add_buffer(buffer, CHAT_MSG['tool_complete_message'].format(step=step+1, tool_json=tool_json), is_debug)
            tool, tool_input = tool_json.tool, tool_json.tool_input
            tool_output = self._tool_use(tool, tool_input)
            if tool_output:
                self._add_buffer(buffer, CHAT_MSG['tool_output_message'].format(step=step+1, tool_output=tool_output), is_debug)
                continue
            if tool_output is None:
                raise ValueError(f"Tool '{tool}' not found in available tools.")

    # Validation step: check if the output is valid
    def _validation_step(self, buffer, is_debug):
        _input = [HumanMessage(content="\n".join(buffer))]
        validation = self.validation_chain.invoke({"input": _input})
        validation_message = validation.message
        if validation.is_valid:
            self._add_buffer(buffer, CHAT_MSG['validation_true_message'].format(validation_message=validation_message), is_debug)
            return True
        else:
            self._add_buffer(buffer, CHAT_MSG['validation_false_message'].format(validation_message=validation_message), is_debug)
            return False

    # Response step: generate and print the final response, update memory, and handle save request
    def _response_step(self, buffer, is_debug, accepted):
        if not accepted:
            self._add_buffer(buffer, CHAT_MSG['max_attempt_exceeded_message'], is_debug)
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
        self.memory.extend([HumanMessage(content="\n".join(buffer)), AIMessage(content=response)])
        if self.save_request:
            self.memory.save_memory()
            self.save_request = False
        return response
    
    # Main chat loop: orchestrate planning, tool, validation, and response steps
    def chat(self, user_input: str, is_debug=False):
        _buffer = []
        recursion = 0
        accepted = False
        self._add_buffer(_buffer, CHAT_MSG['input_message'].format(user_input=user_input), is_debug)
        while recursion < self.recursion_limit and not accepted:
            self._add_buffer(_buffer, CHAT_MSG['attempt_message'].format(n_recursion=recursion+1), is_debug)
            plan = self._planning_step(_buffer, is_debug)
            self._tool_step(_buffer, plan, is_debug)
            accepted = self._validation_step(_buffer, is_debug)
            if not accepted:
                recursion += 1
        response = self._response_step(_buffer, is_debug, accepted)
        self.entity_memory.query(self.memory) # Entity Memory Update
        return response