"""Widget model — the embeddable widget a customer creates and manages."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

import enum


class WidgetType(str, enum.Enum):
    """Supported widget types."""
    SIGNUP_FORM = "signup_form"
    CONTACT_FORM = "contact_form"
    CTA_POPOVER = "cta_popover"


class Widget(Base):
    """
    A widget that a customer (tenant) creates. Each widget is tenant-isolated.
    The widget defines the form fields, display options, and type.
    """
    __tablename__ = "widgets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    widget_type: Mapped[WidgetType] = mapped_column(
        SQLEnum(WidgetType), nullable=False, default=WidgetType.CONTACT_FORM
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True, default="")
    # JSON array of field definitions: [{"name": "email", "type": "email", "required": true}, ...]
    form_fields: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    button_text: Mapped[str] = mapped_column(String(100), nullable=False, default="Submit")
    # JSON for display options: {"color": "#333", "position": "bottom-right", ...}
    display_options: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    owner = relationship("User", back_populates="widgets")
    submissions = relationship("Submission", back_populates="widget", cascade="all, delete-orphan")
