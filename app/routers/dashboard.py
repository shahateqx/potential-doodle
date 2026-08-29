"""Dashboard router — authenticated endpoints for viewing submissions and analytics."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.submission import SubmissionResponse, SubmissionStats, GeoBreakdown, WidgetStats
from app.services import submission_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/submissions", response_model=list[SubmissionResponse])
async def list_submissions(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all submissions for the authenticated user's widgets."""
    submissions = await submission_service.get_submissions_for_owner(
        db, current_user.id, limit=limit, offset=offset
    )
    return [SubmissionResponse.model_validate(s) for s in submissions]


@router.get("/stats", response_model=SubmissionStats)
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated submission stats for the authenticated user."""
    stats = await submission_service.get_submission_stats(db, current_user.id)
    return SubmissionStats(**stats)


@router.get("/widgets/{widget_id}/stats", response_model=WidgetStats)
async def get_widget_stats(
    widget_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get stats for a specific widget (tenant-isolated)."""
    stats = await submission_service.get_widget_submission_stats(db, widget_id, current_user.id)
    if stats is None:
        raise HTTPException(status_code=404, detail="Widget not found")
    return WidgetStats(**stats)


@router.get("/geo", response_model=list[GeoBreakdown])
async def get_geo_breakdown(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get geographic breakdown of submissions."""
    breakdown = await submission_service.get_geo_breakdown(db, current_user.id)
    return [GeoBreakdown(**item) for item in breakdown]
