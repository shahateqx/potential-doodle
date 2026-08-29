"""Rate limiter middleware using slowapi.

Limits requests per IP and per widget to prevent abuse.
Returns 429 Too Many Requests when limits are exceeded.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

# Create the limiter instance — used across routers
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
    storage_uri="memory://",
)
