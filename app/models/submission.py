"""Submission model — a form submission from a website visitor."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Submission(Base):
    """
    A submission captured when a visitor fills out a widget form.
    Linked to a widget (and thus to a tenant). Includes geo-enrichment data.
    """
    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    widget_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("widgets.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    # Idempotency key to prevent duplicate submissions
    idempotency_key: Mapped[str] = mapped_column(
        String(255), nullable=True, unique=True, index=True
    )
    # The submitted form data as JSON
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    # Visitor metadata
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)
    # Geo-enrichment data (may be null if all providers fail)
    geo_country: Mapped[str] = mapped_column(String(100), nullable=True)
    geo_city: Mapped[str] = mapped_column(String(100), nullable=True)
    geo_region: Mapped[str] = mapped_column(String(100), nullable=True)
    geo_lat: Mapped[float] = mapped_column(nullable=True)
    geo_lon: Mapped[float] = mapped_column(nullable=True)
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    # Relationships
    widget = relationship("Widget", back_populates="submissions")
