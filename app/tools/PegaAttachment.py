from __future__ import annotations

import asyncio
import time
from collections import deque
from typing import Any

from mcp.server.fastmcp import FastMCP

from app.pega_client import PegaCaseClient
from app.PegaSettings import PegaSettings
 
 
class FixedWindowRateLimiter:

    def __init__(self, limit_per_minute: int, label: str) -> None:

        if limit_per_minute <= 0:

            raise ValueError("limit_per_minute must be > 0")

        self._limit = limit_per_minute

        self._label = label

        self._events: deque[float] = deque()

        self._lock = asyncio.Lock()
 
    async def acquire(self) -> None:

        now = time.monotonic()

        cutoff = now - 60.0
 
        async with self._lock:

            while self._events and self._events[0] <= cutoff:

                self._events.popleft()
 
            if len(self._events) >= self._limit:

                raise RuntimeError(

                    f"Rate limit exceeded for {self._label}: "

                    f"{self._limit} requests per 60 seconds"

                )
 
            self._events.append(now)
 
 
def register_pega_attachment_tool(

    mcp: FastMCP,

    pega_client: PegaCaseClient,

    settings: PegaSettings,

) -> None:

    attachment_limiter = FixedWindowRateLimiter(

        settings.create_calls_per_minute_limit,

        "pega_add_attachment",

    )
 
    @mcp.tool(

        name="pega_add_attachment",

        description=(

            "Add an attachment to an existing Pega case. "

            "Specify the case ID, file name, and base64-encoded file content. "

            "Returns attachment creation result."

        ),

    )

    async def pega_add_attachment(

        case_id: str,

        file_name: str,

        file_content: str,

        content_type: str | None = None,

    ) -> dict[str, Any]:

        await attachment_limiter.acquire()
 
        content_type = content_type or "application/octet-stream"
 
        return await pega_client.add_attachment(

            case_id=case_id,

            file_name=file_name,

            file_content=file_content,

            content_type=content_type,

        )