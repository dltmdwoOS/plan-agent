from agent.tool_registry import special_tool_registry

@special_tool_registry()
class thought:
    name = "thought"
    args_schema = {'message':{'title':'Message', 'type':'string'}}
    description = """
    This tool is a special tool. Instead of executing the tool directly with tool_input, the 'message' tool_input functions as your thought process.
    This tool must be triggered when no other tool is used. It can also be triggered when additional reasoning is needed to respond to the user's question at the current stage.
    In this case, your thought should go into 'message', and that will be delivered to the user.
    
    Args:
        message (str): Your thought.
    """

@special_tool_registry()
class save_chat_memory:
    name = "save_chat_memory"
    args_schema = {'message':{'title':'Message', 'type':'string'}}
    description = """
    This tool is a special tool. Use it when you want to permanently save the conversation history with the user so far.
    
    Args:
        message (str): The user's question or request that triggered this tool (e.g., 'Save our memory.', 'Let's record our conversation so far.').
    """
    
@special_tool_registry()
class clear_chat_memory:
    name = "clear_chat_memory"
    args_schema = {'message':{'title':'Message', 'type':'string'}}
    description = """
    This tool is a special tool. Use it when you want to delete or reset the conversation history with the user so far.
    
    Args:
        message (str): The user's question or request that triggered this tool (e.g., 'Delete the memory.', 'Reset the conversation history so far.')
    """