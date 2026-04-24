# Teamscale Dev Plugin for Claude Code

A [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code) that uses the [`teamscale-dev` CLI](https://docs.teamscale.com/reference/cli/teamscale-dev/) as an MCP server, exposing its commands as tools for Claude Code.

Unlike the other MCP server plugins in this marketplace (which implement their own servers using generated REST clients), this plugin delegates entirely to `teamscale-dev mcp` — the built-in MCP server mode of the Teamscale CLI. No code generation, no runtime dependencies beyond the CLI itself.

## Prerequisites

- [`teamscale-dev`](https://docs.teamscale.com/reference/cli/teamscale-dev/) installed and available on your `PATH`
- A Teamscale instance with API access
- A Teamscale access key (generate one in your Teamscale user profile)

## Installation

This plugin is distributed via the [teamscale-claude-marketplace](../../). See the [marketplace README](../../README.md) for installation instructions.

## Configuration

`teamscale-dev` uses its own configuration sources:

- **`.teamscale.toml`** — project-level configuration file (placed in your repository root). See the [teamscale-dev documentation](https://docs.teamscale.com/reference/cli/teamscale-dev/) for the format.
- **Environment variables**:

  | Variable | Description |
  |---|---|
  | `TEAMSCALE_DEV_SERVERS` | Teamscale server URL(s) |
  | `TEAMSCALE_DEV_USER` | Your Teamscale username |
  | `TEAMSCALE_DEV_ACCESSKEY` | Your Teamscale access key |

Refer to the [teamscale-dev documentation](https://docs.teamscale.com/reference/cli/teamscale-dev/) for full configuration details.

## Plugin structure

```
.claude-plugin/plugin.json   Plugin manifest — declares teamscale-dev mcp as the MCP server
README.md                    This file
```
