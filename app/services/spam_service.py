"""Spam detection service — honeypot field check and heuristics.

The honeypot is a hidden field named 'website' that humans never fill.
If a bot fills it, the submission is silently rejected.
"""

import logging

logger = logging.getLogger(__name__)


def is_spam(honeypot_value: str) -> bool:
    """
    Check if a submission is spam.
    
    The honeypot field ('website') is hidden via CSS in the widget.
    Legitimate users never see or fill it. Bots auto-fill it.
    
    Returns True if the submission should be rejected as spam.
    """
    if honeypot_value and honeypot_value.strip():
        logger.info(f"Honeypot triggered: value='{honeypot_value[:50]}...'")
        return True

    return False
