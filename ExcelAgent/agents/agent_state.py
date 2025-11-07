class AgentState:
    def __init__(self):
        self.thought_history = []
        self.summary_history = []
        self.action_history = []
        self.reflection_thought = ""
        self.completed_requirements = ""
        self.memory = ""
        self.insight = ""
        self.temp_file = "temp"
        self.error_flag = False

        # Runtime configuration (moved here to avoid circular imports)
        self.vl_model_version = "gemini-2.0-flash-exp"
        self.api_url = None
        self.api_token = ""
        self.model_provider = "gemini"  # 'gemini', 'openai', 'deepseek', 'claude'
        self.temperature = 0.0

        # Optional flags used by prompts (defaults can be adjusted by runner)
        self.use_som = False
        self.icon_caption = False
        self.location_info = False

        self._prepare_temp_dir()

    def _prepare_temp_dir(self):
        import os, shutil
        if os.path.exists(self.temp_file):
            shutil.rmtree(self.temp_file)
        os.mkdir(self.temp_file)