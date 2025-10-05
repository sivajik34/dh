from langchain_openai import ChatOpenAI
from utils import common
from .base import LLMStrategy

class OpenAIStrategy(LLMStrategy):
    def initialize(self):
        env_vars = common.get_required_env_vars(["OPENAI-KEY"])
        return ChatOpenAI(
            temperature=self.config.get("temperature", 0),
            openai_api_key=env_vars["OPENAI-KEY"],
            model_name=self.config.get("model", "gpt-4o-mini"),
            max_tokens=self.config.get("max_tokens", 4000)
        )
