import asyncio
from contextlib import asynccontextmanager

import aiomonitor
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from sqladmin import Admin
from app.config import settings

from app import models
from app.api import routers
from app.api.admin import UserAdmin, PlanAdmin, MessageAdmin, SubscriptionAdmin
from app.database import Base, engine, redis_client
from app.api.routers import authentication, base
from app.api.utils.authentication import AdminAuth


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_client.ping()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    loop = asyncio.get_running_loop()
    monitor = aiomonitor.start_monitor(loop=loop, port=50101)
    app.state.monitor = monitor  # Store for shutdown

    yield  # ➡️ Startup complete
    monitor.close()

    await redis_client.close()


def setup_custom_admin(app: FastAPI):
    authentication_backend = AdminAuth(secret_key=settings.admin_key)
    custom_admin = Admin(app, engine, base_url="/admin", authentication_backend=authentication_backend)

    custom_admin.add_view(UserAdmin)
    custom_admin.add_view(SubscriptionAdmin)
    custom_admin.add_view(MessageAdmin)
    custom_admin.add_view(PlanAdmin)

    return custom_admin


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_routers(app: FastAPI):
    prefix = "/api/v1"

    app.include_router(authentication.router, prefix=prefix, tags=["Authentication"])
    app.include_router(base.router, prefix=prefix, tags=["Base"])


def create_app() -> FastAPI:
    app = FastAPI(title="Application", lifespan=lifespan)

    setup_middlewares(app)
    setup_custom_admin(app)
    register_routers(app)
    add_pagination(app)

    return app
