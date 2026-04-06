from __future__ import annotations
 
import json
import os
from dataclasses import dataclass
from typing import Any
 
 
def _env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value or ""
 
 
@dataclass(frozen=True)
class PegaSettings:
    pega_base_url: str
    pega_application_api_base: str
    pega_oauth_token_url: str
    pega_client_id: str
    pega_client_secret: str
    pega_scope: str
    request_timeout_seconds: float
    token_refresh_skew_seconds: int
 
    allowed_case_type_id: str
    allowed_create_process_id: str
    default_origin_channel: str
    default_create_content: dict[str, Any]
    max_create_payload_bytes: int
    create_calls_per_minute_limit: int
 
    @classmethod
    def from_env(cls) -> "PegaSettings":
        base_url = _env("pega-base-url", required=True).rstrip("/")
        application_api_base = _env(
            "PEGA_APPLICATION_API_BASE",
            f"{base_url}/prweb/api/application/v2",
        ).rstrip("/")
        token_url = _env(
            "PEGA_OAUTH_TOKEN_URL",
            f"{base_url}/prweb/PRRestService/oauth2/v1/token",
        ).rstrip("/")
 
        default_create_content = json.loads(
            _env(
                "DEFAULT_CREATE_CONTENT_JSON",
                '{"Description":"Created by MCP server","Priority":"High","Title":"MCP Support Ticket"}',
            )
        )
        if not isinstance(default_create_content, dict):
            raise ValueError("DEFAULT_CREATE_CONTENT_JSON must be a JSON object")
 
        return cls(
            pega_base_url=base_url,
            pega_application_api_base=application_api_base,
            pega_oauth_token_url=token_url,
            pega_client_id=_env("PEGA_CLIENT_ID", required=True),
            pega_client_secret=_env("PEGA_CLIENT_SECRET", required=True),
            pega_scope=_env("PEGA_SCOPE", ""),
            request_timeout_seconds=float(_env("REQUEST_TIMEOUT_SECONDS", "30")),
            token_refresh_skew_seconds=int(_env("TOKEN_REFRESH_SKEW_SECONDS", "60")),
            allowed_case_type_id=_env(
                "ALLOWED_CASE_TYPE_ID",
                "OPDBWT-FXTest-Work-CitizenComplaintCase"
            ),
            allowed_create_process_id=_env("ALLOWED_CREATE_PROCESS_ID", "pyStartCase"),
            default_origin_channel=_env("DEFAULT_ORIGIN_CHANNEL", "Mobile"),
            default_create_content=default_create_content,
            max_create_payload_bytes=int(_env("MAX_CREATE_PAYLOAD_BYTES", "25000")),
            create_calls_per_minute_limit=int(_env("CREATE_CALLS_PER_MINUTE_LIMIT", "20")),
        )