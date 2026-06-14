import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from celery import Celery
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SyncSessionLocal
from app.models import CallRecord, CallSummary, GoogleSheetIntegration, JobStatus, JobStatusEnum, JobType, ProcessingStatus
from app.services.openai_service import OpenAIService
from app.services.ringcentral_service import RingCentralService
from app.services.sheets_service import SheetsService

celery_app = Celery(
    "tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


def get_sync_session() -> Session:
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@celery_app.task(name="tasks.generate_summary_task")
def generate_summary_task(summary_id: str) -> dict:
    session = SyncSessionLocal()
    try:
        result = session.execute(
            select(CallSummary).where(CallSummary.id == uuid.UUID(summary_id))
        )
        summary = result.scalar_one_or_none()
        if not summary:
            return {"error": "Summary not found"}

        summary.processing_status = ProcessingStatus.PROCESSING
        session.flush()

        result = session.execute(
            select(CallRecord).where(CallRecord.id == summary.call_record_id)
        )
        call_record = result.scalar_one_or_none()
        if not call_record:
            summary.processing_status = ProcessingStatus.FAILED
            summary.error_message = "Call record not found"
            return {"error": "Call record not found"}

        job = JobStatus(
            job_type=JobType.SUMMARY_GENERATION,
            status=JobStatusEnum.PROCESSING,
            input_data={"summary_id": summary_id, "call_record_id": str(call_record.id)},
            started_at=datetime.now(timezone.utc),
        )
        session.add(job)
        session.flush()

        try:
            openai_service = OpenAIService()
            transcript = call_record.raw_data or {}
            raw_transcript = transcript.get("transcript", "") if isinstance(transcript, dict) else str(transcript)
            
            result_text = openai_service.summarize_call(
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

            job.status = JobStatusEnum.COMPLETED
            job.output_data = parsed_result
            job.completed_at = datetime.now(timezone.utc)

            session.flush()
            return {"summary_id": summary_id, "status": "completed"}

        except Exception as e:
            summary.processing_status = ProcessingStatus.FAILED
            summary.error_message = str(e)
            job.status = JobStatusEnum.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            session.flush()
            return {"summary_id": summary_id, "error": str(e)}

    finally:
        session.close()


@celery_app.task(name="tasks.sync_to_sheets_task")
def sync_to_sheets_task(integration_id: str) -> dict:
    session = SyncSessionLocal()
    try:
        result = session.execute(
            select(GoogleSheetIntegration).where(
                GoogleSheetIntegration.id == uuid.UUID(integration_id)
            )
        )
        integration = result.scalar_one_or_none()
        if not integration:
            return {"error": "Integration not found"}

        job = JobStatus(
            job_type=JobType.SHEETS_SYNC,
            status=JobStatusEnum.PROCESSING,
            input_data={"integration_id": integration_id},
            started_at=datetime.now(timezone.utc),
        )
        session.add(job)
        session.flush()

        try:
            summaries_result = session.execute(
                select(CallSummary).where(
                    CallSummary.user_id == integration.user_id,
                    CallSummary.processing_status == ProcessingStatus.COMPLETED,
                )
            )
            summaries = summaries_result.scalars().all()

            summaries_data = []
            for summary in summaries:
                call_record_result = session.execute(
                    select(CallRecord).where(CallRecord.id == summary.call_record_id)
                )
                call_record = call_record_result.scalar_one_or_none()
                summaries_data.append({
                    "id": str(summary.id),
                    "summary_text": summary.summary_text,
                    "key_points": summary.key_points or [],
                    "action_items": summary.action_items or [],
                    "sentiment": summary.sentiment,
                    "created_at": summary.created_at.isoformat() if summary.created_at else None,
                    "call_record": {
                        "ringcentral_call_id": call_record.ringcentral_call_id if call_record else None,
                        "direction": call_record.direction if call_record else None,
                        "from_number": call_record.from_number if call_record else None,
                        "to_number": call_record.to_number if call_record else None,
                        "duration_seconds": call_record.duration_seconds if call_record else None,
                    } if call_record else {},
                })

            sheets_service = SheetsService()
            result_data = session.run_sync(
                lambda s: sheets_service.sync_summaries_to_sheet(
                    spreadsheet_id=integration.spreadsheet_id,
                    sheet_name=integration.sheet_name,
                    summaries=summaries_data,
                )
            )

            integration.last_sync_at = datetime.now(timezone.utc)
            job.status = JobStatusEnum.COMPLETED
            job.output_data = result_data
            job.completed_at = datetime.now(timezone.utc)
            session.flush()

            return {
                "integration_id": integration_id,
                "records_synced": result_data.get("records_synced", 0),
                "status": "completed",
            }

        except Exception as e:
            integration.sync_status = "error"
            job.status = JobStatusEnum.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            session.flush()
            return {"integration_id": integration_id, "error": str(e)}

    finally:
        session.close()
