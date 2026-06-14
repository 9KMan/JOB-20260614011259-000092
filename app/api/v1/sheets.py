import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.database import get_async_session_context
from app.models import GoogleSheetIntegration, SyncStatus, User
from app.schemas import (
    GoogleSheetIntegrationCreate,
    GoogleSheetIntegrationListResponse,
    GoogleSheetIntegrationResponse,
    GoogleSheetIntegrationUpdate,
    SyncResponse,
)
from app.worker.tasks import sync_to_sheets_task

router = APIRouter(prefix="/sheets/integrations", tags=["Google Sheets"])


@router.get("", response_model=GoogleSheetIntegrationListResponse)
async def list_integrations(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session_context),
) -> GoogleSheetIntegrationListResponse:
    result = await session.execute(
        select(GoogleSheetIntegration).where(GoogleSheetIntegration.user_id == current_user.id)
    )
    integrations = result.scalars().all()
    return GoogleSheetIntegrationListResponse(
        total=len(integrations),
        integrations=list(integrations),
    )


@router.post("", response_model=GoogleSheetIntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    integration_data: GoogleSheetIntegrationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session_context),
) -> GoogleSheetIntegration:
    integration = GoogleSheetIntegration(
        user_id=current_user.id,
        spreadsheet_id=integration_data.spreadsheet_id,
        sheet_name=integration_data.sheet_name,
        sync_status=SyncStatus.ACTIVE,
    )
    session.add(integration)
    await session.flush()
    await session.refresh(integration)
    return integration


@router.put("/{integration_id}", response_model=GoogleSheetIntegrationResponse)
async def update_integration(
    integration_id: uuid.UUID,
    update_data: GoogleSheetIntegrationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session_context),
) -> GoogleSheetIntegration:
    result = await session.execute(
        select(GoogleSheetIntegration).where(
            GoogleSheetIntegration.id == integration_id,
            GoogleSheetIntegration.user_id == current_user.id,
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )

    if update_data.spreadsheet_id is not None:
        integration.spreadsheet_id = update_data.spreadsheet_id
    if update_data.sheet_name is not None:
        integration.sheet_name = update_data.sheet_name
    if update_data.sync_status is not None:
        integration.sync_status = update_data.sync_status

    await session.flush()
    await session.refresh(integration)
    return integration


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session_context),
) -> None:
    result = await session.execute(
        select(GoogleSheetIntegration).where(
            GoogleSheetIntegration.id == integration_id,
            GoogleSheetIntegration.user_id == current_user.id,
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )
    await session.delete(integration)


@router.post("/{integration_id}/sync", response_model=SyncResponse)
async def sync_integration(
    integration_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session_context),
) -> SyncResponse:
    result = await session.execute(
        select(GoogleSheetIntegration).where(
            GoogleSheetIntegration.id == integration_id,
            GoogleSheetIntegration.user_id == current_user.id,
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )

    sync_to_sheets_task.delay(str(integration_id))
    
    return SyncResponse(
        success=True,
        message="Sync job queued",
        records_synced=0,
    )