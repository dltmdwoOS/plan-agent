# model.py
PLAN_MODEL_DESC = {
    'plan': (
        "List of dictionaries representing the steps of the plan.\n"
        "Each dictionary includes 'tool' (the action to perform) and 'message' (additional notes).\n"
        "Example: [{'tool': 'get_datetime', 'message': 'Check today's date'}, {'tool': 'web_search', 'message': 'Using the date found in the previous step, search for today's weather in Seoul with a query like 'Month Day Seoul weather'}]\n"
    )
}
TOOL_DECISION_MODEL_DESC = {
    'tool': "Name of the tool to select. Must be one of the currently available tools.",
    'tool_input': "Dictionary of parameters to pass when calling the selected tool.",
    'message': "Reason for selection or notes (optional)"
}
VALIDATION_MODEL_DESC = {
    'is_valid': "Whether the plan and execution were valid. True means the plan was executed successfully; False means it failed and a new plan is needed.",
    'message': "Description message for the validation result. Optional, can provide additional information about the validation result."
}

# graph.py
TOOL_VALIDATOR_MSG = {
    'unexpected_keys'       : "Unexpected keys present: {unexpected_keys}. Allowed keys are {allowed_keys}.",
    'missing_keys'          : "Missing required keys: {missing_keys}.",
    'yaml_path_not_exist'   : "Description file not found for tool: {tool_name}.",
    'yaml_load_error'       : "Failed to load YAML for tool {tool_name}: {e}",
}
SPECIAL_TOOL_MSG = {
    'save_chat_memory'  : "Conversation history has been saved successfully.",
    'clear_chat_memory' : "Conversation history has been reset successfully."
}
CHAT_MSG = {
    'input_message'                 : "Input: {user_input}",
    'attempt_message'               : "\nAttempt {n_recursion}",
    'plan_message'                  : "Plan: {plan}",
    'tool_validation_false_message' : "Step {step} Error : {message}",
    'tool_complete_message'         : "Plan Step {step} Tool: {tool_json}",
    'tool_output_message'           : (
                                        "Plan Step {step} Tool Output:\n"
                                        "<OUTPUT START>\n{tool_output}\n<OUTPUT END>"
                                      ),
    'current_tool_message'          : "Current Step: {tool_json} TODO!",
    'validation_true_message'       : (
                                        "Accepted: True\n"
                                        "Validation Message: {validation_message}"
                                      ),
    'validation_false_message'      : (
                                        "Accepted: False\n"
                                        "Validation Message: {validation_message}\n"
                                        "The above process did not pass validation. You need to re-plan based on the validation result."
                                      ),
    'max_attempt_exceeded_message'  : "Maximum number of attempts exceeded. Further plan resets and tool usage are not possible."
    
}