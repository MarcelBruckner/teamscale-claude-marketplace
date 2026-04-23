# Teamscale Custom MCP Server (TypeScript)

An MCP server that exposes hand-crafted [Teamscale](https://teamscale.com) tools for Claude Code. Uses a generated TypeScript REST API client for type-safe access to the Teamscale API. A [Python implementation](../../teamscale-python-custom/server/) with identical tools is also available.

## Prerequisites

- Node.js 18+
- A Teamscale instance with API access
- A Teamscale access key (generate one in your Teamscale user profile)

## Run locally

1. Install dependencies:

   ```sh
   cd plugins/teamscale-typescript-custom/server
   npm install
   ```

2. Generate the TypeScript API client from the OpenAPI spec:

   ```sh
   ./generate-client.sh
   ```

3. Compile TypeScript:

   ```sh
   npx tsc
   ```

4. Run the server:

   ```sh
   TEAMSCALE_URL=https://myinstance.teamscale.io \
   TEAMSCALE_USER=your-username \
   TEAMSCALE_ACCESS_KEY=your-access-key \
     node dist/server.js
   ```

   The server communicates over stdio (JSON-RPC). It will wait for MCP client input on stdin.

## Install in Claude Code

Add the server to Claude Code:

```sh
claude mcp add teamscale-custom \
  -e TEAMSCALE_URL=<teamscale-url> \
  -e TEAMSCALE_USER=<your-username> \
  -e TEAMSCALE_ACCESS_KEY=<your-access-key> \
  -- node /path/to/teamscale-claude-marketplace/plugins/teamscale-typescript-custom/start-server.js
```

The `start-server.js` script handles client generation, TypeScript compilation, and starting the server automatically.

## Verify Installation

Run `/mcp` in Claude Code to confirm the server is connected and its tools are available.

## Debug

Use the MCP Inspector to test the server standalone:

```sh
TEAMSCALE_URL=https://myinstance.teamscale.io \
TEAMSCALE_ACCESS_KEY=your-access-key \
TEAMSCALE_USER=$(whoami) \
  npx @modelcontextprotocol/inspector -- \
  node /path/to/teamscale-typescript-custom/start-server.js
```

Or, if you already built the server, inspect it directly:

```sh
TEAMSCALE_URL=https://myinstance.teamscale.io \
TEAMSCALE_ACCESS_KEY=your-access-key \
TEAMSCALE_USER=$(whoami) \
  npx @modelcontextprotocol/inspector -- \
  node /path/to/teamscale-typescript-custom/server/dist/server.js
```
