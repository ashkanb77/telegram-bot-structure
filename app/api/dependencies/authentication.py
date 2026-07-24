from typing import Annotated

import jwt
from fastapi import Depends, status, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import DatabaseSessionDep
from app.models import User

http_bearer = HTTPBearer()


async def get_current_user_with_token(
        db: DatabaseSessionDep,
        credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
) -> User:
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError as e:
        raise credentials_exception

    stmt = select(User).where(User.id == user_id).options(selectinload(User.active_subscription))
    result = await db.execute(stmt)

    user = result.scalars().one_or_none()

    if user is None:
        raise credentials_exception

    return user


AuthUserDep = Annotated[User, Depends(get_current_user_with_token)]
