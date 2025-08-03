import logging
from tavily import TavilyClient
from agent.tool_registry import common_tool_registry
from agent.utils import load_locale_const

const = load_locale_const()

TOP_K = 4
try:
    tavily: TavilyClient | None = TavilyClient()
except Exception as e:
    tavily = None
    print("[tool:skip] TavilyClient init failed → 'web_search' not registered:", e)
    
if tavily:
    @common_tool_registry(
        name_or_callable="web_search",
        description=const.WEB_SEARCH_CONST['desc']
    )
    def web_search(query: str) -> str:
        results = tavily.search(
            query=query,
            max_results=TOP_K,
            search_depth="basic"
        )["results"]
        
        return "\n".join([
            const.WEB_SEARCH_CONST['result_format'].format(
                idx=i+1,
                title=r['title'],
                url=r['url'],
                content=r['content']
            ) for i, r in enumerate(results)
        ])