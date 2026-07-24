from typing import Optional, Sequence, Callable

from langchain_core.tools import BaseTool

from app.config import settings
from app.services.models.llm import LLM


class LLMFactory:
    def __init__(self, tools_list: Optional[Sequence[BaseTool | Callable]] = None):
        self._llm = LLM(
            model=settings.llm_model_name, base_url=settings.chatbot_base_url,
            api_key=settings.chatbot_api_key, temperature=settings.llm_temperature,
            max_retries=settings.llm_max_retry, provider=settings.chatbot_provider
        )

        if tools_list:
            self._llm = self._llm.bind_tools(tools_list)

    def get_llm(self):
        return self._llm
