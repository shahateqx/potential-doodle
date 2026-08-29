"""Submission service — business logic for storing and querying submissions."""

import uuid
import logging
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.submission import Submission
from app.models.widget import Widget
from app.services.geo_service import enrich_ip
from app.services.email_service import send_notification_email
from app.services.spam_service import is_spam

logger = logging.getLogger(__name__)


async def create_submission(
    db: AsyncSession,
    widget_id: uuid.UUID,
    data: dict,
    ip_address: str,
    user_agent: str,
    honeypot_value: str = "",
    idempotency_key: Optional[str] = None,
) -> Optional[Submission]:
    """
    Process and store a submission:
    1. Check honeypot (spam)
    2. Check idempotency
    3. Geo-enrich the IP
    4. Store the submission
    5. Trigger safe side effects (email)
    """

    # 1. Spam check — honeypot field filled = bot
    if is_spam(honeypot_value):
        logger.info(f"Spam submission blocked for widget {widget_id}")
        return None  # Silently drop

    # 2. Idempotency check
    if idempotency_key:
        existing = await db.execute(
            select(Submission).where(Submission.idempotency_key == idempotency_key)
        )
        existing_sub = existing.scalar_one_or_none()
        if existing_sub:
            return existing_sub  # Return existing, don't create duplicate

    # 3. Geo-enrichment with fallback chain
    geo_data = await enrich_ip(ip_address)

    # 4. Store the submission
    submission = Submission(
        widget_id=widget_id,
        data=data,
        ip_address=ip_address,
        user_agent=user_agent,
        idempotency_key=idempotency_key,
        geo_country=geo_data.get("country"),
        geo_city=geo_data.get("city"),
        geo_region=geo_data.get("region"),
        geo_lat=geo_data.get("lat"),
        geo_lon=geo_data.get("lon"),
    )
    db.add(submission)
    await db.flush()
    await db.refresh(submission)

    # 5. Safe side effect — email notification (failure must NOT block success)
    try:
        await send_notification_email(widget_id, submission.id, data)
    except Exception as e:
        logger.warning(f"Email side effect failed (non-blocking): {e}")

    return submission


async def get_submissions_for_owner(
    db: AsyncSession, owner_id: uuid.UUID, limit: int = 50, offset: int = 0
) -> List[Submission]:
    """Get all submissions for widgets owned by a tenant."""
    result = await db.execute(
        select(Submission)
        .join(Widget, Submission.widget_id == Widget.id)
        .where(Widget.owner_id == owner_id)
        .order_by(Submission.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_submission_stats(db: AsyncSession, owner_id: uuid.UUID) -> dict:
    """Get aggregated submission stats for a tenant's widgets."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)

    base_query = (
        select(func.count(Submission.id))
        .join(Widget, Submission.widget_id == Widget.id)
        .where(Widget.owner_id == owner_id)
    )

    total = (await db.execute(base_query)).scalar() or 0
    today = (await db.execute(base_query.where(Submission.created_at >= today_start))).scalar() or 0
    week = (await db.execute(base_query.where(Submission.created_at >= week_start))).scalar() or 0
    month = (await db.execute(base_query.where(Submission.created_at >= month_start))).scalar() or 0

    return {
        "total_submissions": total,
        "submissions_today": today,
        "submissions_this_week": week,
        "submissions_this_month": month,
    }


async def get_widget_submission_stats(
    db: AsyncSession, widget_id: uuid.UUID, owner_id: uuid.UUID
) -> dict:
    """Get stats for a specific widget (tenant-isolated)."""
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=7)

    # Verify widget belongs to owner
    widget_check = await db.execute(
        select(Widget).where(Widget.id == widget_id, Widget.owner_id == owner_id)
    )
    widget = widget_check.scalar_one_or_none()
    if not widget:
        return None

    total = (await db.execute(
        select(func.count(Submission.id)).where(Submission.widget_id == widget_id)
    )).scalar() or 0

    recent = (await db.execute(
        select(func.count(Submission.id))
        .where(Submission.widget_id == widget_id, Submission.created_at >= week_start)
    )).scalar() or 0

    return {
        "widget_id": widget_id,
        "widget_title": widget.title,
        "total_submissions": total,
        "recent_submissions": recent,
    }


async def get_geo_breakdown(db: AsyncSession, owner_id: uuid.UUID) -> list:
    """Get geo breakdown for a tenant's submissions."""
    result = await db.execute(
        select(Submission.geo_country, func.count(Submission.id).label("count"))
        .join(Widget, Submission.widget_id == Widget.id)
        .where(Widget.owner_id == owner_id, Submission.geo_country.isnot(None))
        .group_by(Submission.geo_country)
        .order_by(func.count(Submission.id).desc())
        .limit(20)
    )
    return [{"country": row.geo_country, "count": row.count} for row in result.all()]
