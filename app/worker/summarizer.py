import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SyncSessionLocal
from app.models import CallRecord, CallSummary, ProcessingStatus, Sentiment
from app.services.openai_service import OpenAIService


class Summarizer:
    def __init__(self):
        self.openai_service = OpenAIService()

    def process_call_summary(self, summary_id: uuid.UUID) -> dict:
        session = SyncSessionLocal()
        try:
            result = session.execute(
                select(CallSummary).where(CallSummary.id == summary_id)
            )
            summary = result.scalar_one_or_none()
            if not summary:
                return {"error": "Summary not found"}

            result = session.execute(
                select(CallRecord).where(CallRecord.id == summary.call_record_id)
            )
            call_record = result.scalar_one_or_none()
            if not call_record:
                summary.processing_status = ProcessingStatus.FAILED
                summary.error_message = "Call record not found"
                session.flush()
                return {"error": "Call record not found"}

            summary.processing_status = ProcessingStatus.PROCESSING
            session.flush()

            transcript = call_record.raw_data or {}
            raw_transcript = transcript.get("transcript", "") if isinstance(transcript, dict) else str(transcript)

            result_text = self.openai_service.summarize_call(
                call_transcript=raw_transcript or "No transcript available",
                call_metadata={
                    "duration": call_record.duration_seconds,
                    "direction": call_record.direction,
                    "from": call_record.from_number,
                    "to": call_record.to_number,
                },
            )

            parsed_result = json.loads(result_text) if isinstance(result_text, str) else result_text

            summary.summary_text = parsed_result.get("summary", "")
            summary.key_points = parsed_result.get("key_points", [])
            summary.action_items = parsed_result.get("action_items", [])
            summary.sentiment = parsed_result.get("sentiment", "neutral")
            summary.ai_model = "openai-gpt-4o"
            summary.processing_status = ProcessingStatus.COMPLETED
            session.flush()

            return {
                "summary_id": str(summary_id),
                "status": "completed",
                "sentiment": summary.sentiment,
            }

        except Exception as e:
            if summary:
                summary.processing_status = ProcessingStatus.FAILED
                summary.error_message = str(e)
                session.flush()
            return {"summary_id": str(summary_id), "error": str(e)}
        finally:
            session.close()

    def generate_batch_summaries(self, user_id: uuid.UUID, limit: int = 10) -> list[dict]:
        session = SyncSessionLocal()
        try:
            result = session.execute(
                select(CallRecord)
                .where(CallRecord.user_id == user_id)
                .order_by(CallRecord.created_at.desc())
                .limit(limit)
            )
            call_records = result.scalars().all()

            results = []
            for call_record in call_records:
                existing = session.execute(
                    select(CallSummary).where(
                        CallSummary.call_record_id == call_record.id,
                        CallSummary.user_id == user_id,
                    )
                )
                summary = existing.scalar_one_or_none()

                if not summary:
                    summary = CallSummary(
                        call_record_id=call_record.id,
                        user_id=user_id,
                        processing_status=ProcessingStatus.PENDING,
                    )
                    session.add(summary)
                    session.flush()
                    session.refresh(summary)

                    result = self.process_call_summary(summary.id)
                    results.append(result)

            return results
        finally:
            session.close()
