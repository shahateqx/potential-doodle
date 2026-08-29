"""Widget service — business logic for widget CRUD operations."""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.widget import Widget
from app.schemas.widget import WidgetCreate, WidgetUpdate
from app.config import settings


async def create_widget(db: AsyncSession, owner_id: uuid.UUID, data: WidgetCreate) -> Widget:
    """Create a new widget for a tenant."""
    widget = Widget(
        owner_id=owner_id,
        widget_type=data.widget_type,
        title=data.title,
        description=data.description,
        form_fields=[f.model_dump() for f in data.form_fields],
        button_text=data.button_text,
        display_options=data.display_options.model_dump(),
    )
    db.add(widget)
    await db.flush()
    await db.refresh(widget)
    return widget


async def get_widgets(db: AsyncSession, owner_id: uuid.UUID) -> List[Widget]:
    """Get all widgets for a tenant (tenant-isolated)."""
    result = await db.execute(
        select(Widget).where(Widget.owner_id == owner_id).order_by(Widget.created_at.desc())
    )
    return list(result.scalars().all())


async def get_widget(db: AsyncSession, widget_id: uuid.UUID, owner_id: uuid.UUID) -> Optional[Widget]:
    """Get a single widget, enforcing tenant isolation."""
    result = await db.execute(
        select(Widget).where(Widget.id == widget_id, Widget.owner_id == owner_id)
    )
    return result.scalar_one_or_none()


async def get_widget_public(db: AsyncSession, widget_id: uuid.UUID) -> Optional[Widget]:
    """Get a widget by ID (public — for config endpoint, no tenant filter)."""
    result = await db.execute(select(Widget).where(Widget.id == widget_id))
    return result.scalar_one_or_none()


async def update_widget(
    db: AsyncSession, widget_id: uuid.UUID, owner_id: uuid.UUID, data: WidgetUpdate
) -> Optional[Widget]:
    """Update a widget, enforcing tenant isolation."""
    widget = await get_widget(db, widget_id, owner_id)
    if not widget:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if "form_fields" in update_data and update_data["form_fields"] is not None:
        update_data["form_fields"] = [f.model_dump() if hasattr(f, "model_dump") else f for f in data.form_fields]
    if "display_options" in update_data and update_data["display_options"] is not None:
        update_data["display_options"] = data.display_options.model_dump()

    for key, value in update_data.items():
        setattr(widget, key, value)

    await db.flush()
    await db.refresh(widget)
    return widget


async def delete_widget(db: AsyncSession, widget_id: uuid.UUID, owner_id: uuid.UUID) -> bool:
    """Delete a widget, enforcing tenant isolation."""
    widget = await get_widget(db, widget_id, owner_id)
    if not widget:
        return False
    await db.delete(widget)
    await db.flush()
    return True


def generate_snippet(widget_id: uuid.UUID) -> str:
    """Generate the embed snippet for a widget."""
    base = settings.WIDGET_BASE_URL
    return f'<script src="{base}/widget.js?id={widget_id}"></script>'
