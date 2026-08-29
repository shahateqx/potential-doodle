"""Pydantic schemas for submissions."""

import uuid
from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class SubmissionCreate(BaseModel):
    """Schema for creating a submission from a website visitor."""
    widget_id: uuid.UUID
    data: Dict[str, Any] = Field(..., max_length=50)
    # Honeypot field — should always be empty; bots fill it
    website: str = Field(default="", max_length=500)
    # Optional idempotency key for duplicate prevention
    idempotency_key: Optional[str] = Field(default=None, max_length=255)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "widget_id": "550e8400-e29b-41d4-a716-446655440000",
                    "data": {"email": "visitor@example.com", "name": "Jane Doe"},
                    "website": "",
                }
            ]
        }
    }


class SubmissionResponse(BaseModel):
    """Schema for submission data in API responses."""
    id: uuid.UUID
    widget_id: uuid.UUID
    data: Any
    ip_address: Optional[str] = None
    geo_country: Optional[str] = None
    geo_city: Optional[str] = None
    geo_region: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SubmissionStats(BaseModel):
    """Aggregated stats for the dashboard."""
    total_submissions: int
    submissions_today: int
    submissions_this_week: int
    submissions_this_month: int


class GeoBreakdown(BaseModel):
    """Geo breakdown for dashboard."""
    country: Optional[str]
    count: int


class WidgetStats(BaseModel):
    """Per-widget statistics."""
    widget_id: uuid.UUID
    widget_title: str
    total_submissions: int
    recent_submissions: int
