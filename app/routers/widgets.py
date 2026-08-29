"""Widget router — authenticated CRUD endpoints with tenant isolation."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.widget import WidgetCreate, WidgetUpdate, WidgetResponse, SnippetResponse
from app.services import widget_service

router = APIRouter(prefix="/api/widgets", tags=["widgets"])


@router.post("/", response_model=WidgetResponse, status_code=201)
async def create_widget(
    data: WidgetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new widget for the authenticated user."""
    widget = await widget_service.create_widget(db, current_user.id, data)
    return WidgetResponse.model_validate(widget)


@router.get("/", response_model=list[WidgetResponse])
async def list_widgets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all widgets for the authenticated user (tenant-isolated)."""
    widgets = await widget_service.get_widgets(db, current_user.id)
    return [WidgetResponse.model_validate(w) for w in widgets]


@router.get("/{widget_id}", response_model=WidgetResponse)
async def get_widget(
    widget_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific widget (tenant-isolated)."""
    widget = await widget_service.get_widget(db, widget_id, current_user.id)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    return WidgetResponse.model_validate(widget)


@router.put("/{widget_id}", response_model=WidgetResponse)
async def update_widget(
    widget_id: uuid.UUID,
    data: WidgetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a widget (tenant-isolated)."""
    widget = await widget_service.update_widget(db, widget_id, current_user.id, data)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    return WidgetResponse.model_validate(widget)


@router.delete("/{widget_id}", status_code=204)
async def delete_widget(
    widget_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a widget (tenant-isolated)."""
    deleted = await widget_service.delete_widget(db, widget_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Widget not found")


@router.get("/{widget_id}/snippet", response_model=SnippetResponse)
async def get_snippet(
    widget_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the embed snippet for a widget."""
    widget = await widget_service.get_widget(db, widget_id, current_user.id)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    snippet = widget_service.generate_snippet(widget_id)
    return SnippetResponse(widget_id=widget_id, snippet=snippet)
