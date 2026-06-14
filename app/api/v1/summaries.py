import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.database import get_async_session_context
from app.models import CallRecord, CallSummary, ProcessingStatus, User
from app.schemas import (
    CallSummaryListResponse,
    CallSummaryResponse,
    SummaryGenerateRequest,
    SummaryStatusResponse,
)
from app.services.ringcentral_service import RingCentralService
from app.worker.tasks import generate_summary_task

router = APIRouter(prefix="/summaries", tags=["Summaries"])


@router.get("", response_model=CallSummaryListResponse)
async def list_summaries(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session_context),
    limit: int = 50,
    offset: int = 0,
) -> CallSummaryListResponse:
    result = await session.execute(
        select(CallSummary)
        .where(CallSummary.user_id == current_user.id)
        .order_by(CallSummary.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    summaries = result.scalars().all()
    
    count_result = await session.execute(
        select(CallSummary).where(CallSummary.user_id == current_user.id)
    )
    total = len(count_result.scalars().all())
    
    return CallSummaryListResponse(total=total, summaries=list(summaries))


@router.get("/{summary_id}", response_model=CallSummaryResponse)
async def get_summary(
    summary_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session_context),
) -> CallSummary:
    result = await session.execute(
        select(CallSummary).where(
            CallSummary.id == summary_id,
            CallSummary.user_id == current_user.id,
        )
    )
    summary = result.scalar_one_or_none()
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found",
        )
    return summary


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_summary(
    request: SummaryGenerateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session_context),
) -> dict:
    result = await session.execute(
        select(CallRecord).where(
            CallRecord.id == request.call_record_id,
            CallRecord.user_id == current_user.id,
        )
    )
    call_record = result.scalar_one_or_none()
    if not call_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call record not found",
        )
    
    existing = await session.execute(
        select(CallSummary).where(
            CallSummary.call_record_id == request.call_record_id,
            CallSummary.user_id == current_user.id,
        )
    )
    summary = existing.scalar_one_or_none()
    
    if not summary:
        summary = CallSummary(
            call_record_id=request.call_record_id,
            user_id=current_user.id,
            processing_status=ProcessingStatus.PENDING,
        )
        session.add(summary)
        await session.flush()
        await session.refresh(summary)
    
    generate_summary_task.delay(str(summary.id))
    
    return {"message": "Summary generation started", "summary_id": str(summary.id)}


@router.get("/{summary_id}/status", response_model=SummaryStatusResponse)
async def get_summary_status(
    summary_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session_context),
) -> CallSummary:
    result = await session.execute(
        select(CallSummary).where(
            CallSummary.id == summary_id,
            CallSummary.user_id == current_user.id,
        )
    )
    summary = result.scalar_one_or_none()
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found",
        )
    return summary
