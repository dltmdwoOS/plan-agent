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
ENTITIES_MODEL_DESC = {
    'entities': (
        "Dictionary of entities extracted from the conversation. "
        "Keys are entity names or types (e.g., 'person', 'location', 'goal'), values are their details. "
        "Example: { 'person': 'John', 'location': 'Seoul', 'goal': 'Find weather info' }"
    )
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
    'current_tool_message'          : "Current Step: {tool_json} TODO!\nCurrent Entity Memory:\n<ENTITY MEMORY START>\n{entity_memory}\n<ENTITY MEMORY END>",
    'tool_validation_false_message' : "Step {step} Error : {message}",
    'tool_complete_message'         : "Plan Step {step} Tool: {tool_json}",
    'tool_output_message'           : (
                                        "Plan Step {step} Tool Output:\n"
                                        "<OUTPUT START>\n{tool_output}\n<OUTPUT END>"
                                      ),
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

# memory.py
MEMORY_CONST = {
    'summary_input': "Summarize the conversation so far.",
    'load_error_message': "An error occurred while loading the conversation history: {e}",
    'save_error_message': "An error occurred while saving the conversation history: {e}",
}
ENTITY_MEMORY_CONST = {
    'query_input_templeate': (
        "Update the entity memory based on the conversation history so far and current entities. "
        "Return only the updated entity memory as a JSON dictionary.\n"
        "Conversation so far:\n{memory}\n"
        "Current Entity Memory:\n{entity_memory}"
    ),
    'desc': (
        "EntityMemoryChain extracts and updates entities from the conversation. "
        "Entities include people, places, organizations, dates, facts, user goals, decisions, or any information worth remembering. "
        "The output is a JSON dictionary of entities."
    )
}

# Tool related
EXECUTE_CODE_CONST = {
    'tabu_import': "❌ Execution denied due to forbidden modules/functions.",
    'forbidden_module': "❌ Forbidden module import detected → Execution denied",
    'parsing_failed': "❌ Code parsing failed",
    'timeout': "⏰ Execution time limit exceeded ({timeout} seconds).",
    'no_output': "✅ Execution complete (no output)",
    'desc': (
        "Executes the given code in the local Python environment.  "
        "Useful for quick tests or 'fast code snippet validation'.\n"
        "(※ Not for production use, security isolation is limited.)\n\n"
        "Args:\n"
        "    code (str): Python code string to execute. If you never use output functions like `print`, nothing will be output or returned.\n"
        "                e.g., 'for i in range(3): print(i)'\n"
        "    timeout (int): Maximum execution time (seconds). If not specified by the user, the default is 5 seconds.\n\n"
        "Returns:\n"
        "    str: Execution result string combining stdout and stderr.  \n"
        "         If there is no output, returns '✅ Execution complete (no output)'.  \n"
        "         If forbidden modules are detected or a timeout occurs, a message explaining the reason is returned."
    ),
}

GET_USER_LOCATION_CONST = {
    'desc': (
        "Determines the user's current location. Useful when the user asks questions like 'Where am I?' or 'What is my current location?'.\n\n"
        "Args:\n"
        "    query (str): User's question or request (e.g., 'Where am I?', 'Tell me my current location')\n\n"
        "Returns:\n"
        "    str: The user's current location information"
    ),
    'no_location': "No location info",
    'result_format': "Current location: latitude {lat}, longitude {lng}."
}

NEARBY_SEARCH_CONST = {
    'desc': (
        "Searches for nearby places based on the user's current location. Useful when the user asks questions like 'cafes nearby', 'restaurants near me', etc.\n\n"
        "Args:\n"
        "    keyword (str): Keyword for the place to search (e.g., 'cafe', 'restaurant')\n"
        "    latlng (dict[str, float]): The user's current location (latitude and longitude)\n"
        "    radius (int): Search radius (in meters). If the user requests 'cafes within 1km', enter 1000. If the user does not specify a radius, the default is 200m.\n\n"
        "Returns:\n"
        "    str: List of nearby places including address and rating for each place"
    ),
    'no_result': "No nearby places found for '{keyword}'.",
    'result_format': "{name} ({vicinity}) Rating : {rating}",
}

WEB_SEARCH_CONST = {
    'desc': (
        "Performs a web search and returns the top k results as a string. (default k=4)\n\n"
        "Args:\n"
        "    query (str): Search query (e.g., 'News headlines from Time magazine on August 12th', 'Meaning of the idiom 無爲轉變')\n\n"
        "Returns:\n"
        "    str: Search results string. (e.g., '1st search result\\nTitle: ...\\nURL: ...\\nContent: ...\\n\\n2nd search result ...')"
    ),
    'result_format': "{idx}st search result\nTitle:   {title}\nURL:     {url}\nContent: {content}\n",
}

GET_DATETIME_CONST = {
    'desc': (
        "Returns the current date and time in the specified format.\n"
        "Useful when the user asks questions related to date and time, or wants the latest information (e.g., 'What time is it now?' 'I'm curious about yesterday's news.').\n\n"
        "Args:\n"
        "    query (str): User's question or request. (e.g., 'What time is it now?' 'I'm curious about yesterday's news.')\n"
        "    format (str): The format of the required datetime information. (e.g., '%Y-%m-%d %H:%M:%S', '%m-%d (%A)')\n\n"
        "Returns:\n"
        "    str: Datetime string in the `format` format"
    ),
}

GET_IMAGE_FROM_SCREEN_CONST = {
    'desc': (
        "Takes a screenshot, saves it as a file, and returns the file path.\n\n"
        "Args:\n"
        "    query (str): User's question or request (e.g., 'Take a screenshot of what I'm seeing now and tell me the filename.', 'Don't you want to see the video I'm watching? Take a screenshot of the current window.')\n\n"
        "Returns:\n"
        "    str: The file path of the screenshot just taken"
    ),
}

GET_IMAGE_FROM_DB_CONST = {
    'desc': (
        "When you want to see a photo used in a previous conversation again, use this tool to get the filename of the photo by using a description or message record at that time as a query.\n\n"
        "Args:\n"
        "    query (str): Query to find the photo (e.g., 'The photo you reacted to as 'a scene from a comic where Superman and Batman are fighting' before', 'The photo of a dog running in front of the blue sea')\n\n"
        "Returns:\n"
        "    str: The file path of the photo found by the query. If the photo is not found or an error occurs, returns an empty string."
    ),
    'not_found': "",
}

VISION_TOOL_CONST = {
    'desc': (
        "Responds using both the user's query and the image at the same time.\n"
        "When the user includes the image file path directly in the question, or when an image is needed in the current context, this tool is called with the image path to obtain a multimodal answer.\n\n"
        "Args:\n"
        "    query (str): User's question or request (e.g., 'Describe this photo.', 'What is the name of the character on the left side of this picture?')\n"
        "    image_path (str): File path of the attached image\n"
        "Returns:\n"
        "    str: Answer to the user's query (using the image)"
    ),
}

THOUGHT_CONST = {
    'desc': (
        "This tool is a special tool. Instead of executing the tool directly with tool_input, the 'message' tool_input functions as your thought process.\n"
        "This tool must be triggered when no other tool is used. It can also be triggered when additional reasoning is needed to respond to the user's question at the current stage.\n"
        "In this case, your thought should go into 'message', and that will be delivered to the user.\n\n"
        "Args:\n"
        "    message (str): Your thought."
    ),
}

SAVE_CHAT_MEMORY_CONST = {
    'desc': (
        "This tool is a special tool. Use it when you want to permanently save the conversation history with the user so far.\n\n"
        "Args:\n"
        "    message (str): The user's question or request that triggered this tool (e.g., 'Save our memory.', 'Let's record our conversation so far.')."
    ),
}

CLEAR_CHAT_MEMORY_CONST = {
    'desc': (
        "This tool is a special tool. Use it when you want to delete or reset the conversation history with the user so far.\n\n"
        "Args:\n"
        "    message (str): The user's question or request that triggered this tool (e.g., 'Delete the memory.', 'Reset the conversation history so far.')"
    ),
}