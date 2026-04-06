from __future__ import annotations

import logging
import os
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from app.config import Settings
from app.health_server import start_health_server
from app.PegaSettings import PegaSettings
from app.Tokenhelper import PegaTokenHelper
from app.pega_client import PegaCaseClient
from app.tools.PegaCreateCase import register_pega_create_case_tool

def _build_auth_kwargs(settings: Settings) -> dict[str, Any]:
    """Return FastMCP auth kwargs when inbound auth is enabled."""
    if not settings.mcp_auth_enabled:
        return {}

    from pydantic import AnyHttpUrl

    from app.auth import EntraTokenVerifier
    from mcp.server.auth.settings import AuthSettings

    logger = logging.getLogger(__name__)
    logger.info("Inbound MCP auth enabled (Entra tenant: %s)", settings.azure_tenant_id)

    verifier = EntraTokenVerifier(
        tenant_id=settings.azure_tenant_id,
        client_id=settings.azure_client_id,
        required_scopes=settings.mcp_auth_required_scopes or None,
    )

    auth_settings = AuthSettings(
        issuer_url=AnyHttpUrl(
            f"https://login.microsoftonline.com/{settings.azure_tenant_id}/v2.0"
        ),
        resource_server_url=AnyHttpUrl(settings.mcp_auth_base_url),
        required_scopes=settings.mcp_auth_required_scopes or None,
    )

    return {"token_verifier": verifier, "auth": auth_settings}


def build_server(settings: Settings) -> FastMCP:
    auth_kwargs = _build_auth_kwargs(settings)

    mcp = FastMCP(
        settings.server_name,
        host=settings.mcp_host,
        port=settings.mcp_port,
        streamable_http_path=settings.mcp_path,
        **auth_kwargs,
    )

    @mcp.tool(
        name="server_health",
        description="Returns basic scaffold health information.",
    )
    async def server_health() -> dict[str, object]:
        return {
            "status": "ok",
            "server": settings.server_name,
            "transport": settings.mcp_transport,
            "auth_enabled": settings.mcp_auth_enabled,
        }

    # Initialize Pega components
    pega_settings = PegaSettings.from_env()
    token_helper = PegaTokenHelper(pega_settings)
    pega_client = PegaCaseClient(pega_settings, token_helper)

    # Register Pega tools
    register_pega_create_case_tool(mcp, pega_client, pega_settings)

    return mcp


def main() -> None:
    # Load environment variables from .env file
    load_dotenv()
    settings = Settings.from_env()
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    os.environ["FASTMCP_HOST"] = settings.mcp_host
    os.environ["FASTMCP_PORT"] = str(settings.mcp_port)
    os.environ["FASTMCP_STREAMABLE_HTTP_PATH"] = settings.mcp_path

    mcp = build_server(settings)

    if settings.enable_health_server:
        start_health_server(settings.health_host, settings.health_port)

    if settings.mcp_transport == "stdio":
        mcp.run(transport="stdio")
        return

    if settings.mcp_transport == "sse":
        mcp.run(transport="sse")
        return

    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
