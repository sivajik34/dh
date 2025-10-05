from langchain_ollama import OllamaLLM
from utils import common
from .base import LLMStrategy

class LlamaStrategy(LLMStrategy):
    def initialize(self):
        env_vars = common.get_required_env_vars(["BASE_URL"])
        return OllamaLLM(
            base_url=env_vars["BASE_URL"],
            model="llama3.3:latest",
            max_tokens=4000
        )