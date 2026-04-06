# Generic MCP Server Scaffold

Bare-bones Python MCP server scaffold with:

- `FastMCP` bootstrap
- optional streamable HTTP, SSE, or stdio transport
- optional `/healthz` endpoint for container probes
- optional inbound OAuth2 bearer token validation using Microsoft Entra
- one tiny `server_health` tool for smoke testing

The project intentionally contains no business logic and no outbound API integration. Future teams can add their own tools and clients on top of this baseline.

## Project Layout

- `app/main.py`: server startup, transport selection, and generic tool registration
- `app/config.py`: runtime and inbound auth configuration
- `app/auth.py`: Entra JWT verification for inbound MCP requests
- `app/health_server.py`: lightweight `/healthz` HTTP server

## Environment Variables

Copy `.env.example` and set what you need:

- `MCP_SERVER_NAME` (default: `generic-mcp-server`)
- `LOG_LEVEL` (default: `INFO`)
- `MCP_TRANSPORT` (`streamable-http`, `sse`, or `stdio`)
- `MCP_HOST` (default: `0.0.0.0`)
- `MCP_PORT` (default: `8000`)
- `MCP_PATH` (default: `/mcp`; used by `streamable-http`)
- `ENABLE_HEALTH_SERVER` (default: `true`)
- `HEALTH_HOST` (default: `0.0.0.0`)
- `HEALTH_PORT` (default: `8081`)

### Inbound MCP Auth (Entra)

These are only required when `MCP_AUTH_ENABLED=true`:

- `MCP_AUTH_ENABLED` (default: `false`)
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_ID`
- `MCP_AUTH_REQUIRED_SCOPES` (optional comma-separated scopes)
- `MCP_AUTH_BASE_URL` (the externally reachable base URL of the server)

## Run Locally

```bash
cd mcp_server
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
python -m app.main
```

## Docker

```bash
cd mcp_server
docker build -t generic-mcp-server:local .
docker run --rm -p 8000:8000 -p 8081:8081 --env-file .env generic-mcp-server:local
```

## Next Step

Add your domain-specific modules under `app/` and register new tools in `app/main.py` when you are ready to build a real server on top of the scaffold.
