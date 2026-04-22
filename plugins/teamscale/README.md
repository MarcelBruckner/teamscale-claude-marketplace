# Teamscale Plugin for Claude Code

A [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code) that exposes the [Teamscale](https://teamscale.com) REST API as MCP resources and tools, auto-generated from the Teamscale OpenAPI spec.

GET endpoints are exposed as MCP resources (or resource templates when they contain path parameters). Non-GET endpoints (POST, PUT, DELETE, etc.) are excluded by default. Set the `ENABLE_TOOLS` environment variable to expose them as MCP tools.

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager
- A Teamscale instance with API access
- A Teamscale access key (generate one in your Teamscale user profile)

## Installation

This plugin is distributed via the [teamscale-claude-marketplace](../../). See the [marketplace README](../../README.md) for installation, standalone setup, and debug instructions.

## Configuration

The plugin requires the following environment variables:

| Variable | Description |
|---|---|
| `TEAMSCALE_URL` | URL of the Teamscale instance (e.g. `https://myinstance.teamscale.io`) |
| `TEAMSCALE_USER` | Your Teamscale username |
| `TEAMSCALE_ACCESS_KEY` | Your Teamscale access key |
| `ENABLE_TOOLS` | Set to expose non-GET endpoints as MCP tools (optional) |

## Plugin structure

```
.claude-plugin/plugin.json   Plugin manifest — declares the MCP servers
server/                      MCP server (Python, FastMCP + OpenAPI provider)
```
