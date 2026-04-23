# Teamscale Custom Plugin for Claude Code

A [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code) that exposes hand-crafted MCP tools for common [Teamscale](https://teamscale.com) workflows. Uses a generated Python REST API client under the hood.

Unlike the [OpenAPI plugin](../teamscale-fastmcp-openapi/), which auto-generates endpoints from the OpenAPI spec, this plugin provides curated, higher-level tools with custom logic (e.g. findings aggregation, architecture verification, dashboard checks).

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

## Plugin structure

```
.claude-plugin/plugin.json   Plugin manifest — declares the MCP servers
start-server.py              Generates the REST API client and starts the server
server/
  server.py                  MCP server (Python, FastMCP + generated client)
  generate-client.sh         Generates the Python REST API client from the OpenAPI spec
  teamscale-rest-api-client/ Generated Python client
```
