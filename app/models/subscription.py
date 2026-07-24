import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, DateTime, Integer, Enum, Index, text, CheckConstraint, and_
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.config import settings
from app.database import Base
from app.models.base import BaseModelMixin
from app.models.choices import SubscriptionStatus

if TYPE_CHECKING:
    from plan import Plan
    from user import User


class Subscription(BaseModelMixin, Base):
    __tablename__ = 'subscription'

    plan_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("plan.id", ondelete="CASCADE"), nullable=False
    )
    plan: Mapped["Plan"] = relationship(back_populates="subscriptions")

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["User"] = relationship(back_populates="subscriptions")

    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, name="subscription_status_type"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    activated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index(
            "uq_user_active_subscription",
            "user_id",
            unique=True,
            postgresql_where=text(f"status = '{SubscriptionStatus.ACTIVE.value}'")
        ),
        CheckConstraint("used_tokens >= 0"),
        CheckConstraint("activated_at <= expires_at", name="ck_subscription_dates")
    )

    @classmethod
    def valid_subscription(cls):
        now = datetime.datetime.now(settings.timezone)
        return and_(Subscription.expires_at > now, Subscription.status == SubscriptionStatus.ACTIVE)
