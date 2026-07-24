import asyncio
import logging
import os

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from sqlalchemy import select

from app.bot.handlers.start import start_router
from app.bot.middlewares.database import DatabaseMiddleware
from app.database import AsyncSessionLocal
from app.models import Plan
from app.models.choices import UserRegisteredFromType

logging.getLogger(__name__)
load_dotenv()

TELEGRAM_TOKEN = os.getenv('BOT_TOKEN', '')
BALE_TOKEN = os.getenv('BALE_TOKEN', '')


def create_bot(token: str, bot_type: str) -> Bot:
    if bot_type == "telegram":
        return Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    if bot_type == "bale":
        api = TelegramAPIServer(
            base="https://tapi.bale.ai/bot{token}/{method}",
            file="https://tapi.bale.ai/file/bot{token}/{path}",
        )
        session = AiohttpSession(api=api)
        return Bot(token, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    raise ValueError("Unknown bot type")


async def main():
    stmt = select(Plan)
    async with AsyncSessionLocal() as session:
        result = await session.execute(stmt)
        plans = result.scalars().all()
        plans = {plan.name: plan for plan in plans}

    dp = Dispatcher(registered_from=UserRegisteredFromType.TELEGRAM, plans=plans)

    dp.update.middleware(DatabaseMiddleware())
    dp.include_router(start_router)

    bot = create_bot(TELEGRAM_TOKEN, bot_type="telegram")

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
