import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import String, ForeignKey, DateTime, Integer, Text, CheckConstraint, BigInteger
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import BaseModelMixin

if TYPE_CHECKING:
    from user import User


class Message(BaseModelMixin, Base):
    __tablename__ = "message"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["User"] = relationship(back_populates="messages")

    content: Mapped[str] = mapped_column(Text, nullable=False)

    answer: Mapped[str] = mapped_column(Text, nullable=True)
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    used_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    model: Mapped[str] = mapped_column(String(32), nullable=False)
    telegram_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (
        CheckConstraint("(answer IS NULL) = (answered_at IS NULL)", name="ck_answer_consistency"),
        CheckConstraint("used_tokens >= 0"),
    )
