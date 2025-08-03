from agent.tool_registry import special_tool_registry
from agent.utils import load_locale_const

const = load_locale_const()

@special_tool_registry()
class thought:
    name = "thought"
    args_schema = {'message':{'title':'Message', 'type':'string'}}
    description = const.THOUGHT_CONST['desc']

@special_tool_registry()
class save_chat_memory:
    name = "save_chat_memory"
    args_schema = {'message':{'title':'Message', 'type':'string'}}
    description = const.SAVE_CHAT_MEMORY_CONST['desc']
    
@special_tool_registry()
class clear_chat_memory:
    name = "clear_chat_memory"
    args_schema = {'message':{'title':'Message', 'type':'string'}}
    description = const.CLEAR_CHAT_MEMORY_CONST['desc']