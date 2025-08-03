import datetime
from agent.tool_registry import common_tool_registry
from agent.utils import load_locale_const

const = load_locale_const()

@common_tool_registry(
    name_or_callable="get_datetime",
    description=const.GET_DATETIME_CONST['desc']
)
def get_datetime(query: str, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    now = datetime.datetime.now()
    return now.strftime(format)
