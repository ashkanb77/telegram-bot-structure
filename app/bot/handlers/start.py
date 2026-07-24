from typing import Dict

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.main_menu import main_menu
from app.constants import WELCOME_MESSAGE
from app.models import User, Plan
from app.models.choices import UserRegisteredFromType

start_router = Router()


@start_router.message(CommandStart())
async def start(message: Message, registered_from: UserRegisteredFromType, plans: Dict[str, Plan],
                session: AsyncSession):
    phone_number = message.contact.phone_number if message.contact else None
    user = await User.save_user(message.from_user, message.chat.id, phone_number, registered_from, session)
    await user.get_or_create_user_subscription(plans, session)
    await session.commit()
    await message.answer(WELCOME_MESSAGE, reply_markup=main_menu)
