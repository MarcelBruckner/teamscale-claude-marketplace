# Teamscale MCP Server

An MCP server that exposes the [Teamscale](https://teamscale.com) REST API for Claude Code, auto-generated from the instance's OpenAPI spec.

GET endpoints are exposed as MCP resources (or resource templates when they contain path parameters). Non-GET endpoints (POST, PUT, DELETE, etc.) are excluded by default. Set the `ENABLE_TOOLS` environment variable to expose them as MCP tools.

## Prerequisites

- Python with [uv](https://docs.astral.sh/uv/)
- A Teamscale instance with API access
- A Teamscale access key (generate one in your Teamscale user profile)

## Install

Add the server to Claude Code:

```sh
claude mcp add <mcp-name> \
  -e TEAMSCALE_URL=<teamscale-url> \
  -e TEAMSCALE_USER=<your-username> \
  -e TEAMSCALE_ACCESS_KEY=<your-access-key> \
  -- uv run /path/to/teamscale-claude-marketplace/plugins/teamscale/server/server.py
```

**Example:**

```sh
claude mcp add my-teamscale \
  -e TEAMSCALE_URL=https://myinstance.teamscale.io \
  -e TEAMSCALE_USER=$(whoami) \
  -e TEAMSCALE_ACCESS_KEY=xxx \
  -- uv run /path/to/teamscale-claude-marketplace/plugins/teamscale/server/server.py
```

## Verify Installation

Run `/mcp` in Claude Code to confirm the server is connected and its tools are available.

## Debug

Use the MCP Inspector to test the server standalone:

```sh
TEAMSCALE_URL=https://myinstance.teamscale.io TEAMSCALE_ACCESS_KEY=... TEAMSCALE_USER=$(whoami) \
  npx @modelcontextprotocol/inspector -- \
  uv run server.py
```
