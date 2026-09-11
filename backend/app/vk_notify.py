import logging
import random

import httpx

from .config import settings

logger = logging.getLogger("vk_notify")

API_URL = "https://api.vk.com/method/messages.send"


def is_configured() -> bool:
    return bool(settings.vk_bot_token)


async def send_message(vk_user_id: str, text: str) -> bool:
    if not is_configured():
        logger.debug("VK_BOT_TOKEN not set, skipping notification to %s", vk_user_id)
        return False
    if not vk_user_id:
        return False

    params = {
        "access_token": settings.vk_bot_token,
        "v": settings.vk_api_version,
        "user_id": vk_user_id,
        "message": text[:4000],
        "random_id": random.randint(1, 2**31 - 1),
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(API_URL, data=params)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError:
        logger.warning("VK notification request to %s failed", vk_user_id, exc_info=True)
        return False

    if "error" in payload:
        logger.warning("VK notification to %s rejected: %s", vk_user_id, payload["error"])
        return False
    return True
