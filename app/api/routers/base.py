from typing import Dict

import requests
from fastapi import APIRouter, status, HTTPException

from app.config import settings
from app.database import DatabaseSessionDep

router = APIRouter(prefix="/base", tags=["Base"])


@router.get(path="/health-check/backend-health-status", status_code=status.HTTP_200_OK)
async def get_session_list(session: DatabaseSessionDep, ) -> Dict[str, str]:
    return {"status": "Ok"}


@router.get(path="/health-check/chat-api-connection-health-status", status_code=status.HTTP_200_OK)
async def get_session_list(session: DatabaseSessionDep) -> Dict[str, str]:
    try:
        requests.post(settings.chatbot_base_url, timeout=15)
        return {"status": "ok"}
    except:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable")
