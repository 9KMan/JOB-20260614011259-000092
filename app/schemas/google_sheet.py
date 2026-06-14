import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SyncStatusEnum(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


class GoogleSheetIntegrationBase(BaseModel):
    spreadsheet_id: str
    sheet_name: str = "Sheet1"


class GoogleSheetIntegrationCreate(GoogleSheetIntegrationBase):
    pass


class GoogleSheetIntegrationUpdate(BaseModel):
    spreadsheet_id: Optional[str] = None
    sheet_name: Optional[str] = None
    sync_status: Optional[SyncStatusEnum] = None


class GoogleSheetIntegrationResponse(GoogleSheetIntegrationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    last_sync_at: Optional[datetime] = None
    sync_status: SyncStatusEnum
    created_at: datetime
    updated_at: datetime


class GoogleSheetIntegrationListResponse(BaseModel):
    total: int
    integrations: list[GoogleSheetIntegrationResponse]


class SyncResponse(BaseModel):
    success: bool
    message: str
    records_synced: int = 0
