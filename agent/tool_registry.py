from langchain.tools import tool
from agent.utils import export_tool_desc

class CommonToolRegistry(dict): # For Common Tools
    def __call__(self, *d_args, **d_kwargs):
        def wrapper(fn):
            t = tool(*d_args, **d_kwargs)(fn)
            self[t.name] = t
            export_tool_desc(t, kind='common')
            return t
        return wrapper

class SpecialToolRegistry(dict): # For Special Tools
    def __call__(self, *d_args, **d_kwargs):
        def wrapper(cls):
            self[cls.name] = cls
            export_tool_desc(cls, kind='special')
            return cls
        return wrapper
    
common_tool_registry = CommonToolRegistry()
special_tool_registry = SpecialToolRegistry()

import agent.tools