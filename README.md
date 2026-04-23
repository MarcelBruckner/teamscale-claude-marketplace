# teamscale-claude-marketplace

A marketplace for Claude Code plugins by the Teamscale team.

## Plugins

| Plugin | Description |
|--------|-------------|
| [`teamscale-fastmcp-openapi`](plugins/teamscale-fastmcp-openapi/) | Auto-generated from the Teamscale OpenAPI spec. Exposes all GET endpoints as MCP resources and optionally all write endpoints as MCP tools. |
| [`teamscale-fastmcp-custom`](plugins/teamscale-fastmcp-custom/) | Hand-crafted MCP tools using a generated Python REST API client. Provides curated, higher-level tools for common Teamscale workflows. |

## Installation

1. Register the marketplace as a plugin source:

   ```
   /plugins marketplace add https://github.com/MarcelBruckner/teamscale-claude-marketplace.git
   ```

2. Install the plugins you need:

   ```
   /plugins install teamscale-fastmcp-openapi
   ```

   or

   ```
   /plugins install teamscale-fastmcp-custom
   ```

3. Reload plugins to apply changes:

   ```
   /reload-plugins
   ```

## Available Tools and Resources

Each plugin README contains the full list of available MCP tools and resources:

- [teamscale-fastmcp-openapi](plugins/teamscale-fastmcp-openapi/README.md#available-resources-and-resource-templates) — auto-generated resources, resource templates, and tools
- [teamscale-fastmcp-custom](plugins/teamscale-fastmcp-custom/README.md#available-tools) — hand-crafted tools

## Configuration

The plugins require environment variables to connect to your Teamscale instance. These must be set **before** launching Claude Code, since the plugin manifest reads them from the shell environment.

| Variable | Required | Description |
|---|---|---|
| `TEAMSCALE_URL` | Yes | URL of your Teamscale instance (e.g. `https://myinstance.teamscale.io`) |
| `TEAMSCALE_USER` | Yes | Your Teamscale username |
| `TEAMSCALE_ACCESS_KEY` | Yes | Your Teamscale access key |
| `ENABLE_TOOLS` | No | OpenAPI plugin only. Set to any value to expose non-GET endpoints (POST, PUT, DELETE, …) as MCP tools. By default only GET endpoints are available as read-only resources. |

**Option A — export in your shell profile** (e.g. `~/.zshrc`, `~/.bashrc`):

```bash
export TEAMSCALE_URL=https://myinstance.teamscale.io
export TEAMSCALE_USER=your-username
export TEAMSCALE_ACCESS_KEY=your-access-key
# Optional: export ENABLE_TOOLS=true
```

Then start Claude Code normally:

```bash
claude
```

**Option B — set inline when launching Claude Code:**

```bash
TEAMSCALE_URL=https://myinstance.teamscale.io \
TEAMSCALE_USER=your-username \
TEAMSCALE_ACCESS_KEY=your-access-key \
  claude
```

To also enable write tools:

```bash
TEAMSCALE_URL=https://myinstance.teamscale.io \
TEAMSCALE_USER=your-username \
TEAMSCALE_ACCESS_KEY=your-access-key \
ENABLE_TOOLS=1 \
  claude
```

## Development

To develop plugins locally, clone the repository and register it as a local marketplace:

```bash
git clone https://github.com/MarcelBruckner/teamscale-claude-marketplace.git
cd teamscale-claude-marketplace
claude
```

Then register the local directory:

```
/plugins marketplace add ./
```

## Standalone MCP server installation

You can also add an MCP server directly to Claude Code without installing the full plugin.

**OpenAPI plugin:**

```sh
claude mcp add teamscale-openapi \
  -e TEAMSCALE_URL=https://myinstance.teamscale.io \
  -e TEAMSCALE_USER=$(whoami) \
  -e TEAMSCALE_ACCESS_KEY=xxx \
  -- uv run /path/to/teamscale-claude-marketplace/plugins/teamscale-fastmcp-openapi/server/server.py
```

**Custom plugin:**

```sh
claude mcp add teamscale-custom \
  -e TEAMSCALE_URL=https://myinstance.teamscale.io \
  -e TEAMSCALE_USER=$(whoami) \
  -e TEAMSCALE_ACCESS_KEY=xxx \
  -- python3 /path/to/teamscale-claude-marketplace/plugins/teamscale-fastmcp-custom/start-server.py
```

### Verify installation

Run `/mcp` in Claude Code to confirm the server is connected and its tools are available.

## Debug

Use the MCP Inspector to test a server standalone:

```sh
TEAMSCALE_URL=https://myinstance.teamscale.io TEAMSCALE_ACCESS_KEY=... TEAMSCALE_USER=$(whoami) \
  npx @modelcontextprotocol/inspector -- \
  uv run plugins/teamscale-fastmcp-openapi/server/server.py
```
