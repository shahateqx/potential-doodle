"""Geo enrichment service — IP to geolocation with provider fallback chain.

Provider A: ip-api.com (free, no key, 45 req/min)
Provider B: ipapi.co (free tier, ~1,000 lookups/day)

If both fail → return empty dict (submission still succeeds without geo data).
"""

import logging
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Timeout for each provider call
GEO_TIMEOUT = 5.0


async def _fetch_provider_a(ip: str) -> dict:
    """Fetch geo data from ip-api.com (Provider A)."""
    if not settings.GEO_PROVIDER_A_ENABLED:
        raise RuntimeError("Provider A is disabled")

    url = f"{settings.GEO_PROVIDER_A_URL}{ip}"
    async with httpx.AsyncClient(timeout=GEO_TIMEOUT) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") == "fail":
            raise RuntimeError(f"Provider A failed: {data.get('message')}")

        return {
            "country": data.get("country"),
            "city": data.get("city"),
            "region": data.get("regionName"),
            "lat": data.get("lat"),
            "lon": data.get("lon"),
        }


async def _fetch_provider_b(ip: str) -> dict:
    """Fetch geo data from ipapi.co (Provider B)."""
    if not settings.GEO_PROVIDER_B_ENABLED:
        raise RuntimeError("Provider B is disabled")

    url = f"{settings.GEO_PROVIDER_B_URL}{ip}/json/"
    async with httpx.AsyncClient(timeout=GEO_TIMEOUT) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

        if data.get("error"):
            raise RuntimeError(f"Provider B failed: {data.get('reason')}")

        return {
            "country": data.get("country_name"),
            "city": data.get("city"),
            "region": data.get("region"),
            "lat": data.get("latitude"),
            "lon": data.get("longitude"),
        }


async def enrich_ip(ip: str) -> dict:
    """
    Try Provider A → Provider B → empty dict.
    A failing provider degrades the response but never destroys it.
    """
    # Skip enrichment for localhost / private IPs
    if ip in ("127.0.0.1", "::1", "localhost") or ip.startswith("192.168.") or ip.startswith("10."):
        logger.info(f"Skipping geo enrichment for local IP: {ip}")
        return {}

    # Try Provider A
    try:
        geo = await _fetch_provider_a(ip)
        logger.info(f"Geo enriched via Provider A for {ip}: {geo.get('country')}")
        return geo
    except Exception as e:
        logger.warning(f"Provider A failed for {ip}: {e}")

    # Fallback to Provider B
    try:
        geo = await _fetch_provider_b(ip)
        logger.info(f"Geo enriched via Provider B for {ip}: {geo.get('country')}")
        return geo
    except Exception as e:
        logger.warning(f"Provider B also failed for {ip}: {e}")

    # All providers down — degrade gracefully, never fail
    logger.error(f"All geo providers failed for {ip}. Submission will proceed without geo data.")
    return {}
