import logging
from tavily import TavilyClient
from agent.tool_registry import common_tool_registry

TOP_K = 4
try:
    tavily: TavilyClient | None = TavilyClient()
except Exception as e:
    tavily = None
    print("[tool:skip] TavilyClient init failed → 'web_search' not registered:", e)
    
if tavily:
    @common_tool_registry(
        name_or_callable="web_search",
        description="""
        Performs a web search and returns the top k results as a string. (default k=4)
        
        Args:
            query (str): Search query (e.g., 'News headlines from Time magazine on August 12th', 'Meaning of the idiom 無爲轉變')
        
        Returns:
            str: Search results string. (e.g., '1st search result\nTitle: ...\nURL: ...\nContent: ...\n\n2nd search result ...')
        """
    )
    def web_search(query: str) -> str:
        results = tavily.search(
            query=query,
            max_results=TOP_K,
            search_depth="basic"
        )["results"]
        
        return "\n".join(
            f"{i+1}st search result\n"
            f"Title:   {r['title']}\n"
            f"URL:     {r['url']}\n"
            f"Content: {r['content']}\n"
            for i, r in enumerate(results)
        )