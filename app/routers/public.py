"""Public router — widget delivery endpoints (no auth required).

Serves:
- widget.js: The embeddable JavaScript (versioned, long cache)
- Widget config: JSON config for a specific widget (short cache, CORS)
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.widget import WidgetConfigResponse
from app.services import widget_service

router = APIRouter(tags=["public"])

# Path to the widget.js file
WIDGET_JS_PATH = Path(__file__).parent.parent / "static" / "widget.js"

# Version for cache busting
WIDGET_VERSION = "1.0.0"


@router.get("/widget.js")
async def serve_widget_js():
    """
    Serve the embeddable widget JavaScript.
    
    Versioned bundle: long Cache-Control (1 year for immutable assets).
    New version = new URL via ?v= parameter.
    """
    if not WIDGET_JS_PATH.exists():
        raise HTTPException(status_code=404, detail="Widget script not found")

    return FileResponse(
        path=WIDGET_JS_PATH,
        media_type="application/javascript",
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",
            "X-Widget-Version": WIDGET_VERSION,
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.get("/api/widgets/{widget_id}/config")
async def get_widget_config(
    widget_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Public config endpoint for a widget.
    
    Short-lived cache (5 minutes) so config changes propagate quickly.
    CORS headers allow any origin to fetch this.
    """
    widget = await widget_service.get_widget_public(db, widget_id)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

    config = WidgetConfigResponse(
        id=widget.id,
        widget_type=widget.widget_type,
        title=widget.title,
        description=widget.description,
        form_fields=widget.form_fields,
        button_text=widget.button_text,
        display_options=widget.display_options,
    )

    return JSONResponse(
        content=config.model_dump(mode="json"),
        headers={
            "Cache-Control": "public, max-age=300",
            "Access-Control-Allow-Origin": "*",
        },
    )
