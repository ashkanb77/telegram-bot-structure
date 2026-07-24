from typing import List
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, BigInteger, Integer, SmallInteger, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModelMixin

if TYPE_CHECKING:
    from subscription import Subscription


class Plan(BaseModelMixin, Base):
    __tablename__ = 'plan'
    name: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    subscriptions: Mapped[List["Subscription"]] = relationship(back_populates="plan", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("tokens >= 0"),
        CheckConstraint("sort_order >= 0"),
    )
