import os
from openai import OpenAI
from genai_apis import call_genaiapi

class AgentBase:
    def __init__(self, genai_model: str, temperature: float, device: str=None):
        self.genai_model = genai_model
        
        self.history: list = []
        self.system_message: str = None

        self.tools = []

        self.critiques: str = []
        self.user_modification: str = None

        self.opensource_models = ["deepseek", "llama"]
        self.closedsource_models = ["openai", "gemini", "claude"]

        self.temperature = temperature

        self.device = device

        self.base_url = None
        self.api_key = None

        if self.genai_model.startswith("openai"):
            self.api_key = os.getenv("OPENAI_API_KEY")

        elif self.genai_model.startswith("gemini"):
            self.base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            self.api_key=os.getenv("GEMINI_API_KEY")

        elif self.genai_model.startswith("claude"):
            self.base_url="https://api.anthropic.com/v1/", 
            self.api_key=os.getenv("CLAUDE_API_KEY")
        
        elif self.genai_model.startswith("deepseek"):
            #TODO
            pass
        
        else:
            self.base_url="http://localhost:11434/v1/", 
            self.api_key="ollama"

        self.ai_client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )


    def set_system_message(self, sys_msg):
        self.system_message = sys_msg
    

    def __call__(self, message):
        self.history.append({"role": "user", "content": message})
        result = self.execute()
        self.history.append({"role": "assistant", "content": result})
        
        return result


    def execute(self):
        if any([self.genai_model.startswith(_) for _ in self.closedsource_models]):
            response = call_genaiapi(SYSTEM_PROMPT=self.system_message, 
                                     CHATS=self.history, 
                                     ai_client=self.ai_client, 
                                     temp=self.temperature, 
                                     genai_model=self.genai_model)
        else:
            # response = call_hf_model(self.genai_model, self.history)
            pass
        
        return response
