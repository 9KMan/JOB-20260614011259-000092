import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SentimentEnum(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class ProcessingStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CallSummaryBase(BaseModel):
    summary_text: Optional[str] = None
    key_points: Optional[list[str]] = None
    action_items: Optional[list[dict]] = None
    sentiment: Optional[SentimentEnum] = None
    ai_model: Optional[str] = None


class CallSummaryCreate(BaseModel):
    call_record_id: uuid.UUID
    user_id: uuid.UUID


class CallSummaryUpdate(BaseModel):
    summary_text: Optional[str] = None
    key_points: Optional[list[str]] = None
    action_items: Optional[list[dict]] = None
    sentiment: Optional[SentimentEnum] = None


class CallSummaryResponse(CallSummaryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    call_record_id: uuid.UUID
    user_id: uuid.UUID
    processing_status: ProcessingStatusEnum
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CallSummaryListResponse(BaseModel):
    total: int
    summaries: list[CallSummaryResponse]


class SummaryGenerateRequest(BaseModel):
    call_record_id: uuid.UUID


class SummaryStatusResponse(BaseModel):
    id: uuid.UUID
    processing_status: ProcessingStatusEnum
    error_message: Optional[str] = None
