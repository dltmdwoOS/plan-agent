from agent.model.chain_config import ChainConfig

def get_llm(chain_config: ChainConfig, tags: list, **kwargs):
    name, model_family, model_name = chain_config.name, chain_config.model_family, chain_config.model_name
    if model_family=='openai':
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            name=name,
            model_name=model_name,
            **kwargs
        ).with_config(tags=tags)
    elif model_family=='groq':
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            name=name,
            model_name=model_name,
            **kwargs
        ).with_config(tags=tags)
    else:
        raise Exception("Unexpected model family.")
    
    return llm