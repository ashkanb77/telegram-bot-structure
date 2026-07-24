from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import User


class CurrentUserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
            event: Any,
            data: Dict[str, Any],
    ):
        session = data["session"]
        plans = data["plans"]

        if isinstance(event, Message):
            telegram_user = event.from_user

            stmt = select(User).where(User.telegram_id == telegram_user.id).options(
                selectinload(User.active_subscription)
            )

            user = await session.scalar(stmt)
            await user.get_or_create_user_subscription(plans, session)

            data["user"] = user

        return await handler(event, data)
