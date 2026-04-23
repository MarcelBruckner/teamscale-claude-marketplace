# Teamscale Custom Plugin for Claude Code (TypeScript)

A [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code) that exposes hand-crafted MCP tools for common [Teamscale](https://teamscale.com) workflows. Uses a generated REST API client under the hood for type-safe access to the Teamscale API.

This plugin provides curated, higher-level tools with custom logic (e.g. findings aggregation, architecture verification, dashboard checks), unlike the [OpenAPI plugin](../teamscale-python-openapi/) which auto-generates endpoints from the OpenAPI spec.

A [Python implementation](../teamscale-python-custom/) with identical tools is also available. Choose whichever language fits your environment.

## Available Tools

| Tool | Description |
|---|---|
| `list_projects` | List all projects on a Teamscale instance |
| `get_project_id` | Find the Teamscale project ID(s) for a given repository URL |
| `get_project_connectors` | Return the raw connector options for a project |
| `get_project_branches` | Get all live branches for a project |
| `get_worker_logs` | Get all worker log entries for a project |
| `get_worker_log_warnings` | Get warning-level worker log entries (excludes fatals) |
| `get_worker_log_fatals` | Get fatal worker log entries |
| `get_findings_count_per_file` | Count findings per file (spot outliers) |
| `get_findings_count_per_check` | Count findings per check type (spot noisy checks) |
| `get_findings_list` | Fetch all findings for a project |
| `verify_project_dashboards` | Verify existence of overview, system, and test code dashboards |
| `verify_architecture` | Verify architecture assessments and detect system-to-test dependencies |
| `delete_teamscale_project` | Delete a project including dashboards and assignments |

## Prerequisites

- Node.js 18+
- A Teamscale instance with API access
- A Teamscale access key (generate one in your Teamscale user profile)

## Installation

This plugin is distributed via the [teamscale-claude-marketplace](../../). See the [marketplace README](../../README.md) for installation, standalone setup, and debug instructions.

## Configuration

**All environment variables are optional.** If not set, Claude will ask for the connection details (server URL, user, access key) as tool parameters at runtime. This means you can install and use this plugin without any upfront configuration.

To avoid being prompted every time, you can set the following environment variables before launching Claude Code:

| Variable | Description |
|---|---|
| `TEAMSCALE_URL` | URL of the Teamscale instance (e.g. `https://myinstance.teamscale.io`) |
| `TEAMSCALE_USER` | Your Teamscale username |
| `TEAMSCALE_ACCESS_KEY` | Your Teamscale access key |

## Plugin structure

```
.claude-plugin/plugin.json   Plugin manifest — declares the MCP servers
start-server.js              Generates the REST API client, compiles TypeScript, and starts the server
server/
  server.ts                  MCP server (TypeScript, @modelcontextprotocol/sdk + generated client)
  generate-client.sh         Generates the TypeScript REST API client from the OpenAPI spec
  teamscale-openapi.json     Teamscale OpenAPI 3.0.1 specification
  teamscale-rest-api-client/ Generated TypeScript client (gitignored)
  dist/                      Compiled JavaScript output (gitignored)
```
