from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.constants import END, START
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.store.postgres import AsyncPostgresStore

from app.services.base_agent import BaseAgent
from app.services.agent.states import State
from app.services.llm_factory import LLMFactory
from app.services.agent.nodes.call_model_node import CallModelNode
from app.services.agent.router import Router


class Agent(BaseAgent):
    def __init__(self):
        super().__init__()
        tools_list = []
        self._llm_factory = LLMFactory(tools_list)
        self.tool_node = ToolNode(tools_list)

    async def initialize_agent(self):
        if not self._graph:
            self._graph = await self._create_graph()

    async def aget_state(self, config):
        return await self._graph.aget_state(config)

    async def _create_graph(self) -> CompiledStateGraph:
        connection_pool = await self._get_connection_pool()
        self.checkpointer = AsyncPostgresSaver(connection_pool)
        self.store = AsyncPostgresStore(connection_pool)

        call_model_node = CallModelNode(self._llm_factory)

        router = Router()

        builder = StateGraph(State)

        builder.add_node(call_model_node)

        builder.add_edge(START, 'call_model')
        builder.add_conditional_edges('call_model', router.tools_edge, ['tools', END])

        graph = builder.compile(checkpointer=self.checkpointer, store=self.store)
        return graph
