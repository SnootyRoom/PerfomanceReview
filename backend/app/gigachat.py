import logging
import time
import uuid

import httpx

from .config import settings

logger = logging.getLogger("gigachat")

OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
COMPLETIONS_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

_token_cache: dict[str, str | float | None] = {"token": None, "expires_at": 0}


def is_configured() -> bool:
    return bool(settings.gigachat_auth_key)


async def _get_access_token() -> str | None:
    if not is_configured():
        return None

    cached_token = _token_cache["token"]
    cached_expiry = _token_cache["expires_at"] or 0
    if cached_token and float(cached_expiry) > time.time() + 5:
        return str(cached_token)

    try:
        async with httpx.AsyncClient(verify=settings.gigachat_verify_ssl, timeout=15) as client:
            response = await client.post(
                OAUTH_URL,
                headers={
                    "Authorization": f"Basic {settings.gigachat_auth_key}",
                    "RqUID": str(uuid.uuid4()),
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
                data={"scope": settings.gigachat_scope},
            )
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError:
        logger.exception("GigaChat OAuth request failed")
        return None

    token = payload.get("access_token")
    if not token:
        logger.error("GigaChat OAuth response had no access_token: %s", payload)
        return None

    expires_at_ms = payload.get("expires_at")
    _token_cache["token"] = token
    _token_cache["expires_at"] = expires_at_ms / 1000 if expires_at_ms else time.time() + 25 * 60
    return token


async def complete(system_prompt: str, user_prompt: str) -> str | None:
    token = await _get_access_token()
    if not token:
        return None

    try:
        async with httpx.AsyncClient(verify=settings.gigachat_verify_ssl, timeout=45) as client:
            response = await client.post(
                COMPLETIONS_URL,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                json={
                    "model": settings.gigachat_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.4,
                },
            )
            response.raise_for_status()
            payload = response.json()
        return payload["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError):
        logger.exception("GigaChat completion request failed")
        return None
