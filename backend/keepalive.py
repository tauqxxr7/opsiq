import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)


async def ping_self():
    """Ping the service health endpoint every 14 minutes when SELF_URL is configured."""
    url = os.getenv("SELF_URL", "").strip().rstrip("/")
    if not url:
        logger.info("SELF_URL not set, keep-alive disabled")
        return

    while True:
        await asyncio.sleep(840)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{url}/health")
                logger.info("Keep-alive ping: %s", response.status_code)
        except asyncio.CancelledError:
            raise
        except Exception as error:
            logger.warning("Keep-alive failed: %s", error)