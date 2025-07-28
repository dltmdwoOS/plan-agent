import datetime
from agent.tool_registry import common_tool_registry

@common_tool_registry(
    name_or_callable="get_datetime",
    description="""
    Returns the current date and time in the specified format.
    Useful when the user asks questions related to date and time, or wants the latest information (e.g., 'What time is it now?' 'I'm curious about yesterday's news.').
    
    Args:
        query (str): User's question or request. (e.g., 'What time is it now?' 'I'm curious about yesterday's news.')
        format (str): The format of the required datetime information. (e.g., "%Y-%m-%d %H:%M:%S", "%m-%d (%A)")
    
    Returns:
        str: Datetime string in the `format` format
    """
)
def get_datetime(query: str, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    now = datetime.datetime.now()
    return now.strftime(format)
