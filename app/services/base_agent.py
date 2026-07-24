from typing import Optional

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.postgres import AsyncPostgresStore
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.config import settings


class BaseAgent:
    def __init__(self, ):
        self.connection_pool: Optional[AsyncConnectionPool] = None

        self._graph: Optional[CompiledStateGraph] = None
        self.checkpointer: Optional[AsyncPostgresSaver] = None
        self.store: Optional[AsyncPostgresStore] = None

    async def create_graph(self) -> CompiledStateGraph:
        raise NotImplementedError("create graph not implemented.")

    async def _get_connection_pool(self) -> AsyncConnectionPool:
        if self.connection_pool is None:
            self.connection_pool = AsyncConnectionPool(
                settings.langchain_database_url, open=False, min_size=4, max_size=20, timeout=30, max_lifetime=1800,
                max_idle=600, kwargs={"autocommit": True, "prepare_threshold": 0, 'row_factory': dict_row}
            )
            await self.connection_pool.open()
        return self.connection_pool

    def invoke(self, *args, **kwargs):
        return self._graph.invoke(*args, **kwargs)

    async def ainvoke(self, *args, **kwargs):
        return await self._graph.ainvoke(*args, **kwargs)

    def stream(self, *args, **kwargs):
        return self._graph.stream(*args, **kwargs)

    async def astream(self, *args, **kwargs):
        async for event in self._graph.astream(*args, **kwargs):
            yield event
