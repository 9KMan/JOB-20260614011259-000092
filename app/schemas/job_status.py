import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class JobTypeEnum(str, Enum):
    SUMMARY_GENERATION = "summary_generation"
    SHEETS_SYNC = "sheets_sync"


class JobStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStatusBase(BaseModel):
    job_type: JobTypeEnum
    input_data: Optional[dict] = None


class JobStatusCreate(JobStatusBase):
    pass


class JobStatusResponse(JobStatusBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: JobStatusEnum
    output_data: Optional[dict] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime


class JobStatusListResponse(BaseModel):
    total: int
    jobs: list[JobStatusResponse]
