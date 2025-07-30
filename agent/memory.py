from agent.chains import SummaryChain
from agent.utils import load_chat_memory, save_chat_memory
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    messages_to_dict,
    messages_from_dict
)

class Memory:
    def __init__(self, max_tokens=1e4):
        self.memory = []
        self.load_memory()
        
        self.tokens = self._count_tokens(self.memory)
        self.max_tokens = max_tokens
        self.summary_input = [HumanMessage(content="Summarize the conversation so far.")]
        self.summary_chain = SummaryChain()
        
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
            return f"An error occurred while loading the conversation history: {e}"
    
    def save_memory(self):
        try:
            messages_dict = messages_to_dict(self.memory)
            save_chat_memory(messages_dict)
        except Exception as e:
            return f"An error occurred while saving the conversation history: {e}"
    
    def clear_memory(self):
        self.memory = []
        self.tokens = 0
    