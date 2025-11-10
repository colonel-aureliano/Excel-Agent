import os
from typing import List, Optional

from ..chat.api import _detect_provider_from_url, _resolve_api_key, inference_chat
from ..utils.utils import get_logger

logger = get_logger(__name__)


class SingularAgent:
    """Unified interface for one-shot prompting across multiple LLM providers."""

    DEFAULT_ENV_KEY_MAP = {
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "claude": "CLAUDE_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "nvidia": "NVIDIA_API_KEY",
    }

    DEFAULT_API_URL_MAP = {
        "openai": "https://api.openai.com/v1",
        "gemini": None,
        "deepseek": "https://api.deepseek.com/v1",
        "claude": "https://api.anthropic.com/v1/messages",
        "nvidia": "https://integrate.api.nvidia.com/v1",
    }

    def __init__(
        self,
        model_provider: Optional[str] = "gemini",
        model_name: Optional[str] = "gemini-2.0-flash",
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        temperature: float = 0.0,
    ) -> None:
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.action_bnf_text = self._load_file("action_bnf.txt")

        self.model_provider = (model_provider or "gemini").lower()
        self.model_name = model_name or "gemini-2.0-flash"
        self.api_url = api_url
        self.temperature = temperature

        if self.model_provider in (None, "", "auto"):
            self.model_provider = self._auto_detect_provider()

        self.api_key = api_key or self._lookup_default_api_key(self.model_provider)
        self.api_key = _resolve_api_key(self.api_key)

        if not self.api_key:
            raise ValueError("API key is required to initialize SingularAgent.")

        if not self.api_url:
            self.api_url = self.DEFAULT_API_URL_MAP.get(self.model_provider)

        self.chat_history: List[List] = []
        self.first_chat = True
        self.system_prompt = """
        Imagine that you are given a new pseudo-programming language whose syntax is specified through the attached bnf specification. Know that this programming language is used specifically to manipulate a given excel table. You're smart enough to understand how to use this language (since the essential keywords are all natural language) to program the code that will solve an excel task given by a user. You can assume that there exists an interpreter for this language that can execute your code correctly. Here's one example usage: 

User instruction: Highlight any element from column C that starts with a question mark.
Correct answer: REGEX ^.*$ | SELECT C1:C-1 ; REGEX ^\?.*$ | FORMAT style: backgroundcolor, color: yellow
Explanation: First action is to select column C, that is, first cell of C (C1) until last nonempty cell of C (C-1). Second is format background color to yellow for cells whose value matches the regular expression.

User instruction: Format to bold the elements in column I until row 100 that are greater than 5000. Let me know when you're done.
Correct answer: REGEX ^.*$ | SELECT I1:I100 ; REGEX ^([5-9][0-9]{3}|[1-9][0-9]{4,}).*$ | FORMAT style: Bold ; REGEX ^.*$ | TELLUSER I have formatted to bold the appropriate elements.
Explanation: First action selects column I through the 100th row. Second action uses regular expression to match cells with values greater than 5000 and format them to bold. Third action tells user you're done.

User instruction: Read the values from cells A1 to A5 and tell me what they are.
Correct answer: REGEX ^.*$ | READ A1:A5
Explanation: The action reads the content of cells A1 through A5. Wait for next turn to issue the next command.

Your answer should ONLY include the correct answer. Absolutely no explanations necessarily.
        """+"\n Actions BNF Specification: \n"+self.action_bnf_text

    def _auto_detect_provider(self) -> str:
        if self.api_url:
            return _detect_provider_from_url(self.api_url)
        return "gemini"

    def _lookup_default_api_key(self, provider: str) -> Optional[str]:
        env_var = self.DEFAULT_ENV_KEY_MAP.get(provider)
        if env_var and os.environ.get(env_var):
            return os.environ[env_var]

        if provider == "gemini":
            return os.environ.get("GENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        return None

    def _load_file(self, filename: str) -> str:
        file_path = os.path.join(self.script_dir, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def singular_agent_response(
        self,
        subtask_instruction: str,
        first_n_rows_of_sheet: Optional[str] = None,
        read_context: Optional[str] = None,
    ) -> str:
        first_rows_str = (
            str(first_n_rows_of_sheet)
            if first_n_rows_of_sheet is not None
            else ""
        )
        continuing_prompt = (
            f" NOW, user request is: [{subtask_instruction}]."
        )
        if first_rows_str:
            continuing_prompt += (
                f"\nFIRST FEW ROWS OF THE USER'S SHEET UP TO THE LAST NONEMPTY COLUMN: {first_rows_str}"
            )
        if read_context:
            continuing_prompt += (
                f"\nPREVIOUS READ ACTION RESULTS: {read_context}"
            )

        logger.info("Prompt prepared for model: %s", continuing_prompt)

        if self.first_chat:
            self.chat_history.append(
                ["system", [{"type": "text", "text": self.system_prompt}]]
            )
            self.first_chat = False
        
        user_message = continuing_prompt

        self.chat_history.append(
            ["user", [{"type": "text", "text": user_message}]]
        )

        response_text = inference_chat(
            self.chat_history,
            self.model_name,
            self.api_url,
            self.api_key,
            provider=self.model_provider,
            temperature=self.temperature,
        )

        self.chat_history.append(
            ["assistant", [{"type": "text", "text": response_text}]]
        )

        logger.info("Response from model: %s", response_text)
        return response_text


if __name__ == "__main__":
    agent = SingularAgent()
    subtask_instruction = "Highlight any element from column C that starts with a question mark."
    response_text = agent.singular_agent_response(subtask_instruction)
    print(response_text)

