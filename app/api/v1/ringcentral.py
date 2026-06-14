import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.database import get_async_session_context
from app.models import CallRecord, Direction, User
from app.schemas import CallRecordListResponse, CallRecordResponse
from app.services.ringcentral_service import RingCentralService

router = APIRouter(prefix="/ringcentral", tags=["RingCentral"])

REDIRECT_URI = "https://localhost:3000/api/v1/ringcentral/callback"


@router.get("/auth")
async def get_auth_url(
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    service = RingCentralService()
    auth_url = service.get_oauth_url(REDIRECT_URI)
    return {"auth_url": auth_url}


@router.post("/callback")
async def oauth_callback(
    code: str,
    session: AsyncSession = Depends(get_async_session_context),
    current_user: User = Depends(get_current_user),
) -> dict:
    service = RingCentralService()
    token_data = await service.exchange_code_for_token(code, REDIRECT_URI)
    
    current_user.ringcentral_token = token_data
    await session.flush()
    
    return {"message": "RingCentral account connected successfully"}


@router.get("/calls", response_model=CallRecordListResponse)
async def get_calls(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session_context),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> CallRecordListResponse:
    result = await session.execute(
        select(CallRecord)
        .where(CallRecord.user_id == current_user.id)
        .order_by(CallRecord.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    records = result.scalars().all()
    
    count_result = await session.execute(
        select(CallRecord).where(CallRecord.user_id == current_user.id)
    )
    total = len(count_result.scalars().all())
    
    return CallRecordListResponse(total=total, records=list(records))


@router.post("/webhook", response_model=CallRecordResponse, status_code=status.HTTP_201_CREATED)
async def webhook(
    payload: dict,
    session: AsyncSession = Depends(get_async_session_context),
) -> CallRecord:
    user_id = payload.get("owner_id") or payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing user identification in webhook payload",
        )

    result = await session.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    call_data = payload.get("call", {})
    record = CallRecord(
        user_id=user.id,
        ringcentral_call_id=call_data.get("id", ""),
        direction=Direction(call_data.get("direction", "inbound")),
        from_number=call_data.get("from", {}).get("phoneNumber", ""),
        to_number=call_data.get("to", {}).get("phoneNumber", ""),
        duration_seconds=call_data.get("duration"),
        recording_url=call_data.get("recording", {}).get("uri"),
        call_status=payload.get("call_status", "completed"),
        raw_data=payload,
    )
    session.add(record)
    await session.flush()
    await session.refresh(record)
    
    return record
