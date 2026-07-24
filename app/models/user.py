import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, select, Enum, and_, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, selectinload
from sqlalchemy.orm import relationship

from app.config import settings
from app.database import Base
from app.models import Subscription
from app.models.base import BaseModelMixin
from app.models.choices import UserRegisteredFromType, SubscriptionStatus

if TYPE_CHECKING:
    from message import Message


class User(BaseModelMixin, Base):
    __tablename__ = 'user'

    first_name: Mapped[str] = mapped_column(String(length=64))
    last_name: Mapped[str] = mapped_column(String(length=64), nullable=True)
    username: Mapped[str] = mapped_column(String(length=64), unique=True)
    phone_number: Mapped[str] = mapped_column(String(length=20), unique=True, nullable=True)
    registered_from: Mapped[UserRegisteredFromType] = mapped_column(
        Enum(UserRegisteredFromType, name="user_registered_from_type"), nullable=False
    )
    language_code: Mapped[str] = mapped_column(String(length=16), nullable=True)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    telegram_id: Mapped[Integer] = mapped_column(Integer, unique=True, nullable=True)
    chat_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=True)

    messages: Mapped[List["Message"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    subscriptions: Mapped[List["Subscription"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    active_subscription: Mapped["Subscription | None"] = relationship(
        primaryjoin=lambda: and_(
            User.id == Subscription.user_id,
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.expires_at > func.now(),
        ),
        order_by=lambda: Subscription.expires_at.desc(),
        uselist=False,
        viewonly=True,
    )

    @classmethod
    async def save_user(cls, user, chat_id, phone_number, registered_from, session):

        stmt = select(cls).where(cls.telegram_id == user.id).options(
            selectinload(cls.active_subscription)
        )
        db_user = await session.scalar(stmt)

        if db_user:
            db_user.telegram_id = user.id
            db_user.chat_id = chat_id
            db_user.first_name = user.first_name
            db_user.last_name = user.last_name
            db_user.username = user.username
            db_user.language_code = user.language_code

            if phone_number:
                db_user.phone_number = user.phone_number

            if user.is_premium:
                db_user.is_premium = user.is_premium
        else:
            db_user = cls(
                telegram_id=user.id,
                chat_id=chat_id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                registered_from=registered_from,
                language_code=user.language_code,
                is_premium=user.is_premium,
                phone_number=phone_number,
            )
            session.add(db_user)

        return db_user

    async def get_or_create_user_subscription(self, plans, session: AsyncSession):
        is_created = False
        subscription = self.active_subscription
        now = datetime.datetime.now(tz=settings.timezone)

        if subscription:
            return subscription, is_created

        stmt = (update(Subscription)
                .where(Subscription.user_id == self.id)
                .values(status=SubscriptionStatus.EXPIRED))
        await session.execute(stmt)

        subscription = Subscription(
            user_id=self.id, status=SubscriptionStatus.ACTIVE, plan_id=plans[settings.free_plan_name].id,
            expires_at=now + datetime.timedelta(days=365), activated_at=now,
        )
        session.add(subscription)
        await session.flush()
        is_created = True
        return subscription, is_created
