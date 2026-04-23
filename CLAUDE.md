# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Claude Code plugin marketplace containing three MCP server implementations that expose the Teamscale REST API to Claude Code. All three are distributed via the `.claude-plugin/marketplace.json` plugin system.

## Architecture

Three plugins, each a standalone MCP server under `plugins/`:

| Plugin | Approach | SDK / Framework | API Client |
|--------|----------|-----------------|------------|
| `teamscale-python-openapi` | Auto-generated from OpenAPI spec at startup | FastMCP `OpenAPIProvider` | Built-in (fetches spec from running Teamscale) |
| `teamscale-python-custom` | Hand-crafted tools | `mcp[cli]` (official Python SDK) | `openapi-python-client` (generated from local `teamscale-openapi.json`) |
| `teamscale-typescript-custom` | Hand-crafted tools | `@modelcontextprotocol/sdk` | `@hey-api/openapi-ts` (generated from local `teamscale-openapi.json`) |

The two custom plugins expose identical tools and share the same architecture. Both use a generated REST client from the bundled `teamscale-openapi.json` spec, and both support optional connection params (server/user/access_key) per tool call with env-var fallback.

### Plugin entry flow

Each plugin has a `start-server.{py,js}` at its root that bootstraps the server:
- **Python custom**: runs `generate-client.sh` then `uv run python server.py`
- **TypeScript custom**: runs `npm install` (if needed), `generate-client.sh` + `tsc` (if `dist/` missing), then `node dist/server.js`
- **Python OpenAPI**: launched directly via `uv run python server.py` (no client generation step; fetches OpenAPI spec live from Teamscale)

### Connection handling

- **OpenAPI plugin**: requires `TEAMSCALE_URL`, `TEAMSCALE_USER`, `TEAMSCALE_ACCESS_KEY` env vars; exits on missing.
- **Custom plugins**: env vars optional. Each tool accepts `server`/`user`/`access_key` params; `resolveConnection()` falls back to env vars.

## Build & Run Commands

### Python plugins (require Python 3.14+, uv)

```bash
# Regenerate the Python REST client (from plugins/teamscale-python-custom/server/)
./generate-client.sh

# Run the custom Python server directly
uv run --directory plugins/teamscale-python-custom/server python server.py

# Run the OpenAPI Python server directly
uv run --directory plugins/teamscale-python-openapi/server python server.py
```

### TypeScript plugin (requires Node.js, npm)

```bash
# From plugins/teamscale-typescript-custom/server/
npm install

# Regenerate the TypeScript REST client
./generate-client.sh

# Compile TypeScript
npx tsc

# Run
node dist/server.js
```

### Debug with MCP Inspector

```bash
TEAMSCALE_URL=... TEAMSCALE_USER=... TEAMSCALE_ACCESS_KEY=... \
  npx @modelcontextprotocol/inspector -- \
  uv run plugins/teamscale-python-openapi/server/server.py
```

### Install as Claude Code plugin (local dev)

```
/plugins marketplace add ./
/plugins install teamscale-typescript-custom
/reload-plugins
```

## Key implementation patterns

- **`teamscale_tool` decorator** (Python custom): injects a `fetch` helper that handles HTTP errors generically, then strips `fetch` from the tool's public signature so MCP doesn't expose it as a parameter.
- **`teamscaleFetch` function** (TypeScript custom): same error-handling pattern as the Python decorator but as a standalone async function.
- **`textResult` helper** (TypeScript): wraps return values into the MCP text content format (`{ content: [{ type: "text", text: JSON.stringify(...) }] }`). The Python SDK handles this automatically.
- **OpenAPI route mapping** (Python OpenAPI): `custom_route_mapper` classifies GET endpoints as resources/resource-templates and non-GET as tools (only if `ENABLE_TOOLS` is set, otherwise excluded).
