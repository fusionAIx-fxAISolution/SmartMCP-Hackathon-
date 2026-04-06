from __future__ import annotations
 
import asyncio
import time
from dataclasses import dataclass
 
import httpx
 
from app.PegaSettings import PegaSettings


@dataclass
class TokenState:
    access_token: str
    expires_at_epoch: float


class TokenError(RuntimeError):
    pass
 
 
class PegaTokenHelper:
    def __init__(self, settings: PegaSettings) -> None:
        self._settings = settings
        self._state: TokenState | None = None
        self._lock = asyncio.Lock()
        self._client = httpx.AsyncClient(timeout=settings.request_timeout_seconds)
 
    async def get_valid_token(self) -> str:
        if self._is_token_usable():
            return self._state.access_token  # type: ignore[union-attr]
 
        async with self._lock:
            if self._is_token_usable():
                return self._state.access_token  # type: ignore[union-attr]
            self._state = await self._fetch_new_token()
            return self._state.access_token
 
    async def force_new_token(self) -> str:
        async with self._lock:
            self._state = await self._fetch_new_token()
            return self._state.access_token
 
    def _is_token_usable(self) -> bool:
        if not self._state:
            return False
        return self._state.expires_at_epoch > (
            time.time() + self._settings.token_refresh_skew_seconds
        )
 
    async def _fetch_new_token(self) -> TokenState:
        data: dict[str, str] = {"grant_type": "client_credentials"}
        if self._settings.pega_scope:
            data["scope"] = self._settings.pega_scope
 
        response = await self._client.post(
            self._settings.pega_oauth_token_url,
            data=data,
            auth=(self._settings.pega_client_id, self._settings.pega_client_secret),
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
 
        payload = response.json()
        if not isinstance(payload, dict) or "access_token" not in payload:
            raise TokenError("OAuth token response missing access_token")
 
        expires_in = int(payload.get("expires_in", 300))
        return TokenState(
            access_token=str(payload["access_token"]),
            expires_at_epoch=time.time() + max(expires_in, 60),
        )