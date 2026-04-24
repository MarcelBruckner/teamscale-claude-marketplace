# teamscale-claude-marketplace

Bring Teamscale's code quality analysis directly into your Claude Code workflow. This marketplace provides Claude Code plugins that connect to the [Teamscale](https://teamscale.com) REST API, giving you **skills** — interactive workflows that analyze findings, close test gaps, and fix code quality issues right from the command line.

## Skills

The core of this marketplace. Skills are high-level workflows that combine Teamscale analysis with Claude Code's ability to read, edit, and run code:

| Skill | What it does |
|-------|-------------|
| `/teamscale-skills:pre-commit` | Run Teamscale pre-commit analysis on your uncommitted changes. Shows findings grouped by file with severity, category, and message. |
| `/teamscale-skills:merge-request-findings` | Fetch findings for the merge request on your current branch. Auto-detects the MR, shows added findings and findings in changed code. |
| `/teamscale-skills:fix-findings` | Walk through findings one by one, propose concrete code fixes, and apply them with your confirmation. Works standalone or picks up findings from a prior analysis run. |
| `/teamscale-skills:merge-request-test-gaps` | Show which methods changed in your MR lack test coverage. Displays a tested-ratio summary and per-file detail of untested methods. |
| `/teamscale-skills:close-test-gaps` | For new untested methods, proposes and writes tests matching your project's framework. For modified methods, fetches Teamscale's impacted test suggestions so you know which tests to re-run. |

### Typical workflow

```
/teamscale-skills:merge-request-findings   # see what findings your MR introduced
/teamscale-skills:fix-findings             # fix them interactively
/teamscale-skills:merge-request-test-gaps  # check test coverage gaps
/teamscale-skills:close-test-gaps          # write missing tests / re-run impacted tests
/teamscale-skills:pre-commit               # verify everything before pushing
```

## Installation

1. Register the marketplace:

   ```
   /plugins marketplace add https://github.com/MarcelBruckner/teamscale-claude-marketplace.git
   ```

2. Install the skills and an MCP server (the skills need it for Teamscale API access):

   ```
   /plugins install teamscale-skills
   /plugins install teamscale-dev
   ```

3. Reload:

   ```
   /reload-plugins
   ```

That's it. The MCP server connects to Teamscale automatically if you have `TEAMSCALE_URL`, `TEAMSCALE_USER`, and `TEAMSCALE_ACCESS_KEY` set in your environment. If not, Claude will ask for them at runtime.

## MCP Server Plugins

The skills are powered by MCP server plugins that expose the Teamscale REST API as tools Claude can call. Three implementations are available — choose one:

| Plugin | Description |
|--------|-------------|
| [`teamscale-dev`](plugins/teamscale-dev/) | **Recommended.** Uses the [`teamscale-dev` CLI](https://docs.teamscale.com/reference/cli/teamscale-dev/) as an MCP server. Requires `teamscale-dev` on PATH. |
| [`teamscale-python-custom`](plugins/teamscale-python-custom/) | Hand-crafted MCP tools for Teamscale workflows (Python). |
| [`teamscale-typescript-custom`](plugins/teamscale-typescript-custom/) | Same tools as the Python version, for TypeScript environments. |
| [`teamscale-python-openapi`](plugins/teamscale-python-openapi/) | Auto-generated from the full OpenAPI spec. Exposes all endpoints but less curated. |

The `teamscale-dev` plugin delegates to the built-in MCP server mode of the Teamscale CLI — no code generation or runtime dependencies beyond the CLI itself. The two custom plugins expose identical tools and share the same architecture. Both use a generated REST client from the bundled `teamscale-openapi.json` spec.

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open standard for connecting AI assistants to external tools and data sources. MCP servers expose **tools** (actions the AI can invoke), **resources** (data it can read), and **prompts** (reusable templates) over a lightweight JSON-RPC transport.

For building your own MCP servers, see the [MCP SDK overview](https://modelcontextprotocol.io/docs/sdk). This marketplace uses **Python** with [FastMCP](https://github.com/jlowin/fastmcp) and **TypeScript** with [@modelcontextprotocol/sdk](https://github.com/modelcontextprotocol/typescript-sdk).

## Installation

1. Register the marketplace as a plugin source:

   ```
   /plugins marketplace add https://github.com/MarcelBruckner/teamscale-claude-marketplace.git
   ```

2. Install the plugins you need:

   ```
   /plugins install teamscale-dev
   /plugins install teamscale-skills
   ```

   Other MCP server options (choose one):

   ```
   /plugins install teamscale-python-custom
   /plugins install teamscale-typescript-custom
   /plugins install teamscale-python-openapi
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

## Reference

- [teamscale-skills](plugins/teamscale-skills/README.md) — all available skills
- [teamscale-dev](plugins/teamscale-dev/README.md) — MCP server via teamscale-dev CLI
- [teamscale-python-custom](plugins/teamscale-python-custom/README.md#available-tools) — MCP tools (Python)
- [teamscale-typescript-custom](plugins/teamscale-typescript-custom/README.md#available-tools) — MCP tools (TypeScript)
- [teamscale-python-openapi](plugins/teamscale-python-openapi/README.md#available-resources-and-resource-templates) — auto-generated resources and tools

## Configuration

The plugins can be configured with environment variables to connect to your Teamscale instance.

**The `teamscale-dev` plugin** uses its own configuration: `.teamscale.toml` files and `TEAMSCALE_DEV_*` environment variables. See the [teamscale-dev documentation](https://docs.teamscale.com/reference/cli/teamscale-dev/) for details.

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
marp Presentation.md --pdf --output Presentation.pdf
```
