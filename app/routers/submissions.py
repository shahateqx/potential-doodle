"""Submissions router — public endpoint for cross-origin form submissions.

This is the heart of the public API:
- CORS enabled (preflight handled by middleware)
- Rate limited per IP
- Validates all input at the boundary
- Honeypot spam check
- Geo enrichment with fallback
- Safe email side effect
"""

import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.services import submission_service, widget_service
from app.middleware.rate_limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


@router.post("/", response_model=SubmissionResponse, status_code=201)
@limiter.limit("10/minute")
async def create_submission(
    request: Request,
    data: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Accept a cross-origin form submission from a website visitor.
    
    - Validates payload (Pydantic)
    - Checks honeypot for spam
    - Rate limited (10/min per IP)
    - Geo-enriches the IP
    - Stores the submission
    - Triggers email notification (safe — failure doesn't block)
    """
    # Validate widget exists
    widget = await widget_service.get_widget_public(db, data.widget_id)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

    # Enforce max payload size (reject oversized)
    body = await request.body()
    if len(body) > 10_000:  # 10KB limit
        raise HTTPException(status_code=413, detail="Payload too large")

    # Get client IP
    ip = request.client.host if request.client else "0.0.0.0"
    user_agent = request.headers.get("user-agent", "")

    # Create submission (spam check, geo enrichment, email side effect all happen inside)
    submission = await submission_service.create_submission(
        db=db,
        widget_id=data.widget_id,
        data=data.data,
        ip_address=ip,
        user_agent=user_agent,
        honeypot_value=data.website,
        idempotency_key=data.idempotency_key,
    )

    if submission is None:
        # Spam detected — silently return success to not tip off the bot
        # But actually return a 400 as per PROBE 6 requirements
        raise HTTPException(status_code=400, detail="Submission rejected")

    return SubmissionResponse.model_validate(submission)
