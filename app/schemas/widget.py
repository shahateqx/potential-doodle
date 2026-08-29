"""Pydantic schemas for widget CRUD operations."""

import uuid
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field

from app.models.widget import WidgetType


class FormField(BaseModel):
    """Schema for a single form field definition."""
    name: str = Field(..., min_length=1, max_length=100)
    label: str = Field(..., min_length=1, max_length=200)
    field_type: str = Field(..., pattern="^(text|email|tel|textarea|number|url)$")
    required: bool = True
    placeholder: str = ""


class DisplayOptions(BaseModel):
    """Schema for widget display options."""
    color: str = "#4F46E5"
    background_color: str = "#FFFFFF"
    text_color: str = "#1F2937"
    position: str = "bottom-right"
    border_radius: str = "8px"


class WidgetCreate(BaseModel):
    """Schema for creating a new widget."""
    widget_type: WidgetType = WidgetType.CONTACT_FORM
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=1000)
    form_fields: List[FormField] = Field(
        default=[
            FormField(name="email", label="Email", field_type="email", required=True, placeholder="your@email.com"),
            FormField(name="name", label="Name", field_type="text", required=True, placeholder="Your name"),
        ]
    )
    button_text: str = Field(default="Submit", min_length=1, max_length=100)
    display_options: DisplayOptions = DisplayOptions()


class WidgetUpdate(BaseModel):
    """Schema for updating a widget (all fields optional)."""
    widget_type: Optional[WidgetType] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    form_fields: Optional[List[FormField]] = None
    button_text: Optional[str] = Field(default=None, min_length=1, max_length=100)
    display_options: Optional[DisplayOptions] = None


class WidgetResponse(BaseModel):
    """Schema for widget data in API responses."""
    id: uuid.UUID
    owner_id: uuid.UUID
    widget_type: WidgetType
    title: str
    description: str
    form_fields: Any
    button_text: str
    display_options: Any
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WidgetConfigResponse(BaseModel):
    """Public config served to the embed script (no owner info exposed)."""
    id: uuid.UUID
    widget_type: WidgetType
    title: str
    description: str
    form_fields: Any
    button_text: str
    display_options: Any


class SnippetResponse(BaseModel):
    """The embed snippet for a widget."""
    widget_id: uuid.UUID
    snippet: str
