# Teamscale Custom MCP Server

An MCP server that exposes hand-crafted [Teamscale](https://teamscale.com) tools for Claude Code. Uses a generated Python REST API client for type-safe access to the Teamscale API.

## Prerequisites

- Python with [uv](https://docs.astral.sh/uv/)
- A Teamscale instance with API access
- A Teamscale access key (generate one in your Teamscale user profile)

## Install

Add the server to Claude Code:

```sh
claude mcp add teamscale-custom \
  -e TEAMSCALE_URL=<teamscale-url> \
  -e TEAMSCALE_USER=<your-username> \
  -e TEAMSCALE_ACCESS_KEY=<your-access-key> \
  -- python3 /path/to/teamscale-claude-marketplace/plugins/teamscale-fastmcp-custom/start-server.py
```

## Verify Installation

Run `/mcp` in Claude Code to confirm the server is connected and its tools are available.

## Debug

Use the MCP Inspector to test the server standalone:

```sh
TEAMSCALE_URL=https://myinstance.teamscale.io TEAMSCALE_ACCESS_KEY=... TEAMSCALE_USER=$(whoami) \
  npx @modelcontextprotocol/inspector -- \
  python3 start-server.py
```
