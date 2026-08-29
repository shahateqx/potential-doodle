"""Email service — safe side effect for submission notifications.

Logs to console by default. Can use Mailpit or real SMTP.
CRITICAL: Failure here must NEVER block the submission from being stored.
"""

import uuid
import logging
from typing import Any, Dict

from app.config import settings

logger = logging.getLogger(__name__)


async def send_notification_email(
    widget_id: uuid.UUID, submission_id: uuid.UUID, data: Dict[str, Any]
) -> None:
    """
    Send a notification email about a new submission.
    
    This is a SAFE SIDE EFFECT — if it fails, the submission still succeeds.
    Currently logs to console; can be swapped for real SMTP or Mailpit.
    """
    if not settings.EMAIL_ENABLED:
        logger.info(f"Email disabled. Skipping notification for submission {submission_id}")
        return

    # Log the email (console-based — free, as per capstone requirements)
    logger.info(
        f"📧 EMAIL NOTIFICATION\n"
        f"  To: widget owner\n"
        f"  Subject: New submission on widget {widget_id}\n"
        f"  Submission ID: {submission_id}\n"
        f"  Data: {data}\n"
        f"  From: {settings.SMTP_FROM}"
    )

    # In production, you'd send via SMTP here:
    # try:
    #     message = MIMEText(f"New submission: {data}")
    #     message["Subject"] = f"New submission on widget {widget_id}"
    #     message["From"] = settings.SMTP_FROM
    #     message["To"] = owner_email
    #     async with aiosmtplib.SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT) as smtp:
    #         await smtp.send_message(message)
    # except Exception as e:
    #     logger.warning(f"SMTP send failed: {e}")
    #     raise  # Let the caller handle it safely
