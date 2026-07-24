# app/database.py

from typing import AsyncGenerator, Annotated

import redis.asyncio as redis
from fastapi import Depends
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import declarative_base

from .config import settings

DATABASE_URL = settings.database_url
CONNECT_ARGS = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_async_engine(DATABASE_URL, connect_args=CONNECT_ARGS, echo=False, pool_pre_ping=True)
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(bind=engine, expire_on_commit=False)
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

Base = declarative_base()

with PostgresStore.from_conn_string(settings.langchain_database_url) as store:
    store.setup()

with PostgresSaver.from_conn_string(settings.langchain_database_url) as checkpointer:
    checkpointer.setup()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    try:
        yield redis_client
    finally:
        await redis_client.close()


DatabaseSessionDep = Annotated[AsyncSession, Depends(get_session)]
RedisDep = Annotated[redis.Redis, Depends(get_redis)]
