from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.config import get_store

from app.services.agent.prompts import system_prompt, user_memory_prompt
from app.services.agent.states import State
from app.services.llm_factory import LLMFactory


class CallModelNode:

    def __init__(self, llm_factory: LLMFactory):
        self._llm_factory = llm_factory

    async def __call__(self, state: State, config: RunnableConfig):
        prompt = system_prompt
        user_id = config['configurable']['user_id']
        store = get_store()
        user_info = await store.aget(('users',), str(user_id))

        if user_info:
            user_memory = user_info.value['memory']
            if user_memory:
                user_memory = '\n'.join(user_memory)
                prompt = prompt + user_memory_prompt.format(user_memory=user_memory)

        prompt = [SystemMessage(prompt)] + state['messages']
        llm = self._llm_factory.get_llm(state['model_name'])
        response = await llm.ainvoke(prompt)
        usage_tokens = response.usage_metadata
        last_message_tokens = usage_tokens['input_tokens'] + usage_tokens['output_tokens'] * 7
        used_tokens = state.get('used_tokens', 0) + last_message_tokens

        return {
            'messages': [response], 'used_tokens': used_tokens,
            'last_input_tokens': usage_tokens['input_tokens'], 'last_message_tokens': last_message_tokens
        }
