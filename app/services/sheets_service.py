from datetime import datetime, timezone
from typing import Optional

from google.oauth2 import credentials
from google.oauth2.service_account import Credentials
from googleapiclient import discovery
from googleapiclient.errors import HttpError

from app.config import settings


class SheetsService:
    def __init__(self):
        self._service = None
    
    def _get_service(self):
        if self._service is None:
            creds = credentials.Credentials.from_authorized_user_info(
                info={
                    "client_id": settings.google_sheets_client_id,
                    "client_secret": settings.google_sheets_client_secret,
                }
            )
            self._service = discovery.build("sheets", "v4", credentials=creds)
        return self._service
    
    def _get_service_account_service(self):
        if self._service is None:
            creds = Credentials.from_service_account_file(
                "/path/to/service-account.json"
            )
            self._service = discovery.build("sheets", "v4", credentials=creds)
        return self._service
    
    async def sync_summaries_to_sheet(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        summaries: list[dict],
    ) -> dict:
        service = self._get_service()
        
        if not summaries:
            return {"records_synced": 0}
        
        values = [
            [
                "Date",
                "Call ID",
                "Direction",
                "From",
                "To",
                "Duration (s)",
                "Summary",
                "Key Points",
                "Action Items",
                "Sentiment",
            ]
        ]
        
        for summary in summaries:
            call_record = summary.get("call_record", {})
            values.append([
                summary.get("created_at", ""),
                call_record.get("ringcentral_call_id", ""),
                call_record.get("direction", ""),
                call_record.get("from_number", ""),
                call_record.get("to_number", ""),
                str(call_record.get("duration_seconds", "")),
                summary.get("summary_text", ""),
                ", ".join(summary.get("key_points", [])),
                str(summary.get("action_items", [])),
                summary.get("sentiment", ""),
            ])
        
        try:
            body = {"values": values}
            result = (
                service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet_name}!A:J",
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )
            return {
                "records_synced": result.get("updates", {}).get("updatedRows", 0),
                "spreadsheet_id": spreadsheet_id,
            }
        except HttpError as e:
            raise Exception(f"Failed to sync to Google Sheets: {str(e)}")
    
    async def update_sync_status(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        last_sync_at: datetime,
    ) -> bool:
        return True
