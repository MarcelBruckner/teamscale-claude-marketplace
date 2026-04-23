# teamscale-claude-marketplace

A marketplace for Claude Code plugins by the Teamscale team.

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open standard for connecting AI assistants to external tools and data sources. MCP servers expose **tools** (actions the AI can invoke), **resources** (data it can read), and **prompts** (reusable templates) over a lightweight JSON-RPC transport. The plugins in this marketplace are MCP servers that give Claude Code access to the Teamscale REST API.

### Building your own MCP server

Official SDKs are available in multiple languages, organized into tiers by feature completeness and maintenance commitment:

| Tier | Languages | What it means |
|------|-----------|---------------|
| **Tier 1** | **TypeScript, Python, C#, Go** | Full feature parity, actively maintained by the MCP team |
| Tier 2 | Java, Rust | Approaching full support, actively developed |
| Tier 3 | Swift, Ruby, PHP | Early-stage or community-driven |

**TypeScript** and **Python** are the most mature choices and have the broadest ecosystem of examples and documentation. The plugins in this marketplace use **Python** with the [FastMCP](https://github.com/jlowin/fastmcp) framework and **TypeScript** with the [@modelcontextprotocol/sdk](https://github.com/modelcontextprotocol/typescript-sdk).

For further reading, see the [MCP SDK overview](https://modelcontextprotocol.io/docs/sdk) and the [SDK tiering system](https://modelcontextprotocol.io/community/sdk-tiers).

## Plugins

| Plugin | Description |
|--------|-------------|
| [`teamscale-python-openapi`](plugins/teamscale-python-openapi/) | Auto-generated from the Teamscale OpenAPI spec. Exposes all GET endpoints as MCP resources and optionally all write endpoints as MCP tools. |
| [`teamscale-python-custom`](plugins/teamscale-python-custom/) | Hand-crafted MCP tools for common Teamscale workflows (Python implementation). |
| [`teamscale-typescript-custom`](plugins/teamscale-typescript-custom/) | Hand-crafted MCP tools for common Teamscale workflows (TypeScript implementation). |

The two custom plugins (`teamscale-python-custom` and `teamscale-typescript-custom`) expose identical tools and share the same architecture — choose whichever language fits your environment. Both use a generated REST API client for type-safe access to the Teamscale API.

## Installation

1. Register the marketplace as a plugin source:

   ```
   /plugins marketplace add https://github.com/MarcelBruckner/teamscale-claude-marketplace.git
   ```

2. Install the plugins you need:

   ```
   /plugins install teamscale-python-openapi
   ```

   or

   ```
   /plugins install teamscale-python-custom
   ```

   or

   ```
   /plugins install teamscale-typescript-custom
   ```

3. Reload plugins to apply changes:

   ```
   /reload-plugins
   ```

### Updating

To pull the latest plugin versions from the marketplace:

```
/plugins marketplace update teamscale-plugins
```

Then reinstall any plugin you want to update:

```
/plugins install teamscale-typescript-custom
```

### Local installation (for development)

If you have the repository cloned locally, register it as a local marketplace instead:

```
/plugins marketplace add ./
```

Then install plugins the same way as above. See the [Development](#development) section for more details.

### Troubleshooting

If a plugin fails to start, check for errors in Claude Code:

```
/plugins
```

Navigate to the **Errors** tab to see plugin loading errors (e.g. missing environment variables, failed MCP connections).

To check MCP server connection status, run:

```
/mcp
```

This shows all registered MCP servers and whether they connected successfully or failed.

For detailed logs, start Claude Code in debug mode:

```sh
claude --debug
```

## Available Tools and Resources

Each plugin README contains the full list of available MCP tools and resources:

- [teamscale-python-openapi](plugins/teamscale-python-openapi/README.md#available-resources-and-resource-templates) — auto-generated resources, resource templates, and tools
- [teamscale-python-custom](plugins/teamscale-python-custom/README.md#available-tools) — hand-crafted tools (Python implementation)
- [teamscale-typescript-custom](plugins/teamscale-typescript-custom/README.md#available-tools) — hand-crafted tools (TypeScript implementation)

## Configuration

The plugins can be configured with environment variables to connect to your Teamscale instance.

**For the custom plugins (`teamscale-python-custom` and `teamscale-typescript-custom`), all environment variables are optional.** If not set, Claude will ask for the connection details (server URL, user, access key) as tool parameters at runtime. This means you can install and use the custom plugins without any upfront configuration.

The OpenAPI plugin (`teamscale-python-openapi`) requires the environment variables to be set before launching Claude Code.

| Variable | Required | Description |
|---|---|---|
| `TEAMSCALE_URL` | OpenAPI: Yes, Custom: No | URL of your Teamscale instance (e.g. `https://myinstance.teamscale.io`) |
| `TEAMSCALE_USER` | OpenAPI: Yes, Custom: No | Your Teamscale username |
| `TEAMSCALE_ACCESS_KEY` | OpenAPI: Yes, Custom: No | Your Teamscale access key |
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
  -- uv run /path/to/teamscale-claude-marketplace/plugins/teamscale-python-openapi/server/server.py
```

**Custom plugin (Python):**

```sh
claude mcp add teamscale-custom \
  -e TEAMSCALE_URL=https://myinstance.teamscale.io \
  -e TEAMSCALE_USER=$(whoami) \
  -e TEAMSCALE_ACCESS_KEY=xxx \
  -- python3 /path/to/teamscale-claude-marketplace/plugins/teamscale-python-custom/start-server.py
```

**Custom plugin (TypeScript):**

```sh
claude mcp add teamscale-custom \
  -e TEAMSCALE_URL=https://myinstance.teamscale.io \
  -e TEAMSCALE_USER=$(whoami) \
  -e TEAMSCALE_ACCESS_KEY=xxx \
  -- node /path/to/teamscale-claude-marketplace/plugins/teamscale-typescript-custom/start-server.js
```

### Verify installation

Run `/mcp` in Claude Code to confirm the server is connected and its tools are available.

## Debug

Use the MCP Inspector to test a server standalone:

```sh
TEAMSCALE_URL=https://myinstance.teamscale.io TEAMSCALE_ACCESS_KEY=... TEAMSCALE_USER=$(whoami) \
  npx @modelcontextprotocol/inspector -- \
  uv run plugins/teamscale-python-openapi/server/server.py
```

## Comparison

To generate a PDF of the plugin comparison presentation:

```sh
npx @marp-team/marp-cli comparison.md --html --pdf --output comparison.pdf
```
