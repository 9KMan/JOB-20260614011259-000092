import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DirectionEnum(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallStatusEnum(str, Enum):
    COMPLETED = "completed"
    MISSED = "missed"
    VOICEMAIL = "voicemail"


class CallRecordBase(BaseModel):
    ringcentral_call_id: str
    direction: DirectionEnum
    from_number: str
    to_number: str
    duration_seconds: Optional[int] = None
    recording_url: Optional[str] = None
    call_status: CallStatusEnum
    raw_data: Optional[dict] = None


class CallRecordCreate(CallRecordBase):
    user_id: uuid.UUID


class CallRecordUpdate(BaseModel):
    duration_seconds: Optional[int] = None
    recording_url: Optional[str] = None
    call_status: Optional[CallStatusEnum] = None
    raw_data: Optional[dict] = None


class CallRecordResponse(CallRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class CallRecordListResponse(BaseModel):
    total: int
    records: list[CallRecordResponse]
