from agent_base import AgentBase
from ExcelAgent.chat.api import inference_chat
from ExcelAgent.chat.prompt import get_manager_initial_prompt, get_memory_prompt
from ExcelAgent.chat.chat import init_action_chat, init_reflect_chat, init_memory_chat, add_response
from ExcelAgent.chat.response import action_agent_response, reflect_agent_response

class ManagerAgent(AgentBase):
    def __init__(self, genai_model: str, temperature: float, device: str=None):
        super().__init__(genai_model, temperature, device)
        
        self.role = "manager"
        # TODO get what you need from prompt.py/response.py/chat.py


class ActionAgent(AgentBase):
    def __init__(self, genai_model: str, temperature: float, device: str=None):
        super().__init__(genai_model, temperature, device)
        
        self.role = "action"
        # TODO

class ReflectAgent(AgentBase):
    def __init__(self, genai_model: str, temperature: float, device: str=None):
        super().__init__(genai_model, temperature, device)
        
        self.role = "reflect"
        # TODO