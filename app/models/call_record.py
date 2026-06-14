import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Direction(str, PyEnum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallStatus(str, PyEnum):
    COMPLETED = "completed"
    MISSED = "missed"
    VOICEMAIL = "voicemail"


class CallRecord(Base):
    __tablename__ = "call_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), indexed=True, nullable=False
    )
    ringcentral_call_id: Mapped[str] = mapped_column(String(255), indexed=True, nullable=False)
    direction: Mapped[Direction] = mapped_column(String(20), nullable=False)
    from_number: Mapped[str] = mapped_column(String(50), nullable=False)
    to_number: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    recording_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    call_status: Mapped[CallStatus] = mapped_column(String(20), nullable=False)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="call_records")
    call_summary = relationship("CallSummary", back_populates="call_record", uselist=False)
