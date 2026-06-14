import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.database import get_async_session_context
from app.models import JobStatus, User
from app.schemas import JobStatusListResponse, JobStatusResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=JobStatusListResponse)
async def list_jobs(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session_context),
    limit: int = 50,
    offset: int = 0,
) -> JobStatusListResponse:
    result = await session.execute(
        select(JobStatus)
        .order_by(JobStatus.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    jobs = result.scalars().all()
    
    count_result = await session.execute(select(JobStatus))
    total = len(count_result.scalars().all())
    
    return JobStatusListResponse(total=total, jobs=list(jobs))


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job(
    job_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session_context),
) -> JobStatus:
    result = await session.execute(select(JobStatus).where(JobStatus.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return job