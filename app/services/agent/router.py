from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.constants import END

from app.services.agent.states import State


class Router:

    def tools_edge(self, state: State) -> Literal["end", "tools"]:
        last_message = state['messages'][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            state['messages'][-1].content = 'tools_call'
            return 'tools'
        return END
