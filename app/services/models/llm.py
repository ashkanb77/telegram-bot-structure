from typing import Optional, Any

from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.runnables.utils import Input, Output
from langchain_openai.chat_models import ChatOpenAI


class LLM(Runnable):
    def __init__(
            self, api_key, provider='open-ai', model='gpt-4o-mini',
            temperature=0, base_url=None, max_retries=2, **kwargs
    ):
        self.llm = self._get_llm(
            provider=provider, model=model, api_key=api_key, base_url=base_url,
            temperature=temperature, max_retries=max_retries, **kwargs
        )

    def invoke(self, input: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        return self.llm.invoke(input)

    async def ainvoke(self, input: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        response = await self.llm.ainvoke(input)
        return response

    def _get_llm(
            self, provider, model, api_key, temperature=0, base_url=None, max_retries=2, **kwargs
    ):
        if provider == 'open-ai':
            return ChatOpenAI(
                model=model, temperature=temperature, api_key=api_key, base_url=base_url,
                max_retries=max_retries, **kwargs
            )

    def bind_tools(self, tools_list):
        return self.llm.bind_tools(tools_list)
