from __future__ import annotations

from typing import Any

import httpx

from app.PegaSettings import PegaSettings
from app.Tokenhelper import PegaTokenHelper


class PegaClientError(RuntimeError):
    """Exception raised for Pega API errors"""
    pass


class PegaCaseClient:
    def __init__(self, settings: PegaSettings, token_helper: PegaTokenHelper) -> None:
        self._settings = settings
        self._token_helper = token_helper
        self._client = httpx.AsyncClient(
            base_url=settings.pega_application_api_base,
            timeout=settings.request_timeout_seconds,
        )
 
    async def create_case(
        self,
        payload: dict[str, Any],
        view_type: str = "none",
        page_name: str | None = None,
        origin_channel: str | None = None,
    ) -> dict[str, Any]:
        return await self._request_json(
            "POST",
            "/cases",
            params=self._compact_params({"viewType": view_type, "pageName": page_name}),
            headers_extra=self._compact_headers({"x-origin-channel": origin_channel}),
            json=payload,
        )
 
    async def _request_json(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        headers_extra = kwargs.pop("headers_extra", {})
        headers = self._headers(await self._token_helper.get_valid_token())
        headers.update(headers_extra)
 
        response = await self._client.request(method, path, headers=headers, **kwargs)
 
        if response.status_code == 401:
            new_token = await self._token_helper.force_new_token()
            headers["Authorization"] = f"Bearer {new_token}"
            response = await self._client.request(method, path, headers=headers, **kwargs)
 
        if response.status_code >= 400:
            body = response.text[:500]
            raise PegaClientError(
                f"Pega API request failed with status {response.status_code}: {body}"
            )
 
        if response.status_code == 204 or not response.content:
            return {"status": "ok", "status_code": response.status_code}
 
        payload = response.json()
        if isinstance(payload, dict):
            return payload
        return {"data": payload}
 
    @staticmethod
    def _headers(token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
 
    @staticmethod
    def _compact_params(values: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in values.items() if v is not None}
 
    @staticmethod
    def _compact_headers(values: dict[str, Any]) -> dict[str, str]:
        return {k: str(v) for k, v in values.items() if v is not None}