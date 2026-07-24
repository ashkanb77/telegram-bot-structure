from datetime import datetime, timedelta, timezone

import jwt
from alembic.util import status
from fastapi import HTTPException, status, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.schemas.authentication import RegisterSchema
from app.api.schemas.authentication import TokenResponseSchema, BackendRefreshTokenRequestSchema, LoginSchema
from app.api.schemas.user import BaseUserSchema
from app.config import settings
from app.database import DatabaseSessionDep
from app.models import User, Subscription

router = APIRouter(prefix="/authentication", tags=["Authentication"])


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_lifetime_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_lifetime)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


async def authenticate_user(payload: LoginSchema, session: DatabaseSessionDep) -> BaseUserSchema | None:
    # otp = await check_otp(payload)
    stmt = select(User).where(User.phone_number == payload.phone_number).options(
        selectinload(User.active_subscription).joinedload(Subscription.plan)
    )
    result = await session.execute(stmt)
    user = result.scalars().one()
    return BaseUserSchema(id=user.id, subscription=user.active_subscription)


@router.post(path="/login/register", )
async def register_user(payload: RegisterSchema, session: DatabaseSessionDep):
    # otp = await send_otp(payload)
    return {}


@router.post(path="/login/token", response_model=TokenResponseSchema)
async def login_for_access_token(payload: LoginSchema, session: DatabaseSessionDep) -> TokenResponseSchema:
    user = await authenticate_user(payload, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect token")

    access = create_access_token(data={"sub": str(user.id)})
    refresh = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponseSchema(access_token=access, refresh_token=refresh, token_type="bearer")


@router.post(
    path="/login/refresh",
    response_model=TokenResponseSchema,
)
async def refresh_token(
        refresh: BackendRefreshTokenRequestSchema,
) -> TokenResponseSchema:
    try:
        payload = jwt.decode(refresh.refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    access = create_access_token(data={"sub": user_uuid})
    refresh = create_refresh_token(data={"sub": user_uuid})
    return TokenResponseSchema(access_token=access, refresh_token=refresh, token_type="bearer")
