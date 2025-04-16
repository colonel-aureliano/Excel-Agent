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

        self._prepare_temp_dir()

    def _prepare_temp_dir(self):
        import os, shutil
        if os.path.exists(self.temp_file):
            shutil.rmtree(self.temp_file)
        os.mkdir(self.temp_file)