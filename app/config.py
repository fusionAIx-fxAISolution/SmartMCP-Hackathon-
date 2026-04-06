from __future__ import annotations

import os
from dataclasses import dataclass


def _env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value or ""


@dataclass(frozen=True)
class Settings:
    server_name: str
    log_level: str
    mcp_transport: str
    mcp_host: str
    mcp_port: int
    mcp_path: str
    enable_health_server: bool
    health_host: str
    health_port: int
    mcp_auth_enabled: bool
    azure_tenant_id: str
    azure_client_id: str
    mcp_auth_required_scopes: list[str]
    mcp_auth_base_url: str

    @classmethod
    def from_env(cls) -> "Settings":
        instance = cls(
            server_name=_env("MCP_SERVER_NAME", "generic-mcp-server"),
            log_level=_env("LOG_LEVEL", "INFO").upper(),
            mcp_transport=_env("MCP_TRANSPORT", "streamable-http"),
            mcp_host=_env("MCP_HOST", "0.0.0.0"),
            mcp_port=int(_env("PORT", _env("MCP_PORT", "8000"))),
            mcp_path=_env("MCP_PATH", "/mcp"),
            enable_health_server=_env("ENABLE_HEALTH_SERVER", "true").lower() == "true",
            health_host=_env("HEALTH_HOST", "0.0.0.0"),
            health_port=int(_env("HEALTH_PORT", "8081")),
            mcp_auth_enabled=_env("MCP_AUTH_ENABLED", "false").lower() == "true",
            azure_tenant_id=_env("AZURE_TENANT_ID", ""),
            azure_client_id=_env("AZURE_CLIENT_ID", ""),
            mcp_auth_required_scopes=[
                scope.strip()
                for scope in _env("MCP_AUTH_REQUIRED_SCOPES", "").split(",")
                if scope.strip()
            ],
            mcp_auth_base_url=_env("MCP_AUTH_BASE_URL", "").rstrip("/"),
        )

        if instance.mcp_auth_enabled:
            missing = [
                name
                for name, value in [
                    ("AZURE_TENANT_ID", instance.azure_tenant_id),
                    ("AZURE_CLIENT_ID", instance.azure_client_id),
                    ("MCP_AUTH_BASE_URL", instance.mcp_auth_base_url),
                ]
                if not value
            ]
            if missing:
                missing_vars = ", ".join(missing)
                raise ValueError(
                    "MCP_AUTH_ENABLED=true but missing required variable(s): "
                    f"{missing_vars}"
                )

        return instance
