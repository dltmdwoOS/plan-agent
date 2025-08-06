from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    messages_to_dict,
    messages_from_dict
)
from agent.chains import EntityMemoryChain, SummaryChain
from agent.utils import load_chat_memory, save_chat_memory
from agent.utils import load_locale_const
const = load_locale_const()
MEMORY_CONST = const.MEMORY_CONST
ENTITY_MEMORY_CONST = const.ENTITY_MEMORY_CONST

class Memory:
    def __init__(self, max_tokens=64000):
        self.memory = []
        self.load_memory()
        
        self.tokens = self._count_tokens(self.memory)
        self.max_tokens = max_tokens
        self.summary_input = [HumanMessage(content=MEMORY_CONST['summary_input'])]
        self.summary_chain = SummaryChain()
        
    def __repr__(self):
        result = []
        for msg in self.memory:
            if isinstance(msg, HumanMessage):
                result.append(f' - Human: "{msg.content}"')
            elif isinstance(msg, AIMessage):
                result.append(f' - AI: "{msg.content}"')
        return '\n'.join(result)
    
    def _summarizing(self, is_reset_memory=False):
        out = self.summary_chain.invoke({"memory": self.memory, "input": self.summary_input})
        summary_message = AIMessage(content=out)
        if is_reset_memory: 
            self.memory = [summary_message] # Hard Reset
            self.tokens = self._count_tokens(self.memory)
        return summary_message
        
    def _count_tokens(self, msgs):
        return sum(len(msg.content) for msg in msgs)
    
    def extend(self, message_sequence):
        self.memory.extend(message_sequence)
        self.tokens += self._count_tokens(message_sequence)
        
        if self.tokens > self.max_tokens:
            self._summarizing(is_reset_memory=True)
            
    def load_memory(self):
        try:
            messages_dict = load_chat_memory()
            if messages_dict is not None:
                self.memory = messages_from_dict(messages_dict)
        except Exception as e:
            return MEMORY_CONST['load_error_message'].format(e=e)
    
    def save_memory(self):
        try:
            messages_dict = messages_to_dict(self.memory)
            save_chat_memory(messages_dict)
        except Exception as e:
            return MEMORY_CONST['save_error_message'].format(e=e)
    
    def clear_memory(self):
        self.memory = []
        self.tokens = 0
    
    
class EntityMemory:
    def __init__(self):
        self.entity_memory = [("void", "void")]
        self.entity_memory_chain = EntityMemoryChain()
        self.query_input_templeate = ENTITY_MEMORY_CONST['query_input_templeate']
        
    def query(self, memory):
        query_input = [HumanMessage(self.query_input_templeate.format(memory=memory, entity_memory=self.entity_memory))]
        out = self.entity_memory_chain.invoke({"input": query_input})
        self.entity_memory = out
        
        