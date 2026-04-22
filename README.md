# teamscale-claude-marketplace

A marketplace for Claude Code plugins by the Teamscale team.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/MarcelBruckner/teamscale-claude-marketplace.git
   ```

2. Start Claude Code in the top-level directory:

   ```bash
   cd teamscale-claude-marketplace
   claude
   ```

3. Register the marketplace as a plugin source:

   ```
   /plugin marketplace add ./
   ```

4. Install the plugins you need. Available plugins:

   | Plugin | Description |
   |--------|-------------|
   | [`teamscale`](plugins/teamscale/) | MCP server that exposes the Teamscale REST API as resources and tools (auto-generated from OpenAPI). |

   To install a plugin, run:

   ```
   /plugin install teamscale
   ```

5. Reload plugins to apply changes:

   ```
   /reload-plugins
   ```

## Standalone MCP server installation

You can also add the MCP server directly to Claude Code without installing the full plugin:

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

### Verify installation

Run `/mcp` in Claude Code to confirm the server is connected and its tools are available.

## Debug

Use the MCP Inspector to test the server standalone:

```sh
TEAMSCALE_URL=https://myinstance.teamscale.io TEAMSCALE_ACCESS_KEY=... TEAMSCALE_USER=$(whoami) \
  npx @modelcontextprotocol/inspector -- \
  uv run plugins/teamscale/server/server.py
```
