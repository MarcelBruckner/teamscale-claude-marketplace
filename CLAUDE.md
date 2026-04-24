# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Claude Code plugin marketplace containing MCP server implementations that expose the Teamscale REST API to Claude Code, plus a skills plugin that provides high-level workflows built on those tools. All are distributed via the `.claude-plugin/marketplace.json` plugin system.

## Architecture

Four plugins under `plugins/`:

| Plugin | Type | Description |
|--------|------|-------------|
| `teamscale-dev` | MCP server | Delegates to `teamscale-dev mcp` — the built-in MCP mode of the Teamscale CLI |
| `teamscale-python-openapi` | MCP server | Auto-generated tools from OpenAPI spec at startup |
| `teamscale-python-custom` | MCP server | Hand-crafted tools with `mcp[cli]` + `openapi-python-client` |
| `teamscale-typescript-custom` | MCP server | Hand-crafted tools with `@modelcontextprotocol/sdk` + `@hey-api/openapi-ts` |
| `teamscale-skills` | Skills plugin | Claude Code skills that orchestrate MCP tools into multi-step workflows |

The two custom MCP plugins expose identical tools and share the same architecture. Both use a generated REST client from the bundled `teamscale-openapi.json` spec, and both support optional connection params (server/user/access_key) per tool call with env-var fallback.

### Skills plugin

`teamscale-skills` contains Markdown skill files at `plugins/teamscale-skills/skills/<name>/Skill.md`. Each skill is a YAML-frontmatter Markdown file that instructs Claude Code how to perform a multi-step workflow using MCP tools and built-in tools (Read, Edit, Bash, Glob). Skills do not contain code — they are instructions.

Current skills:
- `pre-commit` — run Teamscale pre-commit analysis on uncommitted changes
- `merge-request-findings` — fetch and present findings for the current MR
- `fix-findings` — propose and apply code fixes for findings with user confirmation
- `merge-request-test-gaps` — show test gap analysis for the current MR
- `close-test-gaps` — propose tests for untested methods / suggest test runs for modified methods

### Plugin entry flow

- **teamscale-dev**: runs `teamscale-dev mcp` directly — no build step, no generated client. Requires `teamscale-dev` on PATH.
- **Python custom**: has a `start-server.py` that runs `generate-client.sh` then `uv run python server.py`
- **TypeScript custom**: has a `start-server.js` that runs `npm install` (if needed), `generate-client.sh` + `tsc` (if `dist/` missing), then `node dist/server.js`
- **Python OpenAPI**: launched directly via `uv run python server.py` (no client generation step; fetches OpenAPI spec live from Teamscale)

### Connection handling

- **teamscale-dev plugin**: uses `.teamscale.toml` files and `TEAMSCALE_DEV_SERVERS`/`TEAMSCALE_DEV_USER`/`TEAMSCALE_DEV_ACCESSKEY` env vars. See [teamscale-dev docs](https://docs.teamscale.com/reference/cli/teamscale-dev/).
- **OpenAPI plugin**: requires `TEAMSCALE_URL`, `TEAMSCALE_USER`, `TEAMSCALE_ACCESS_KEY` env vars; exits on missing.
- **Custom plugins**: env vars optional. Each tool accepts `server`/`user`/`access_key` params; `resolveConnection()` falls back to env vars.

## Build & Run Commands

### Python plugins (require Python 3.14+, uv)

```bash
# Regenerate the Python REST client (from plugins/teamscale-python-custom/server/)
./generate-client.sh

# Run the custom Python server directly
uv run --directory plugins/teamscale-python-custom/server python server.py

# Run the OpenAPI Python server directly
uv run --directory plugins/teamscale-python-openapi/server python server.py
```

### TypeScript plugin (requires Node.js, npm)

```bash
# From plugins/teamscale-typescript-custom/server/
npm install

# Regenerate the TypeScript REST client
./generate-client.sh

# Compile TypeScript
npx tsc

# Run
node dist/server.js
```

### Debug with MCP Inspector

```bash
TEAMSCALE_URL=... TEAMSCALE_USER=... TEAMSCALE_ACCESS_KEY=... \
  npx @modelcontextprotocol/inspector -- \
  uv run plugins/teamscale-python-openapi/server/server.py
```

### Install as Claude Code plugin (local dev)

```
/plugins marketplace add ./
/plugins install teamscale-typescript-custom
/reload-plugins
```

## Key implementation patterns

- **`teamscale_tool` decorator** (Python custom): injects a `fetch` helper that handles HTTP errors generically, then strips `fetch` from the tool's public signature so MCP doesn't expose it as a parameter.
- **`teamscaleFetch` function** (TypeScript custom): same error-handling pattern as the Python decorator but as a standalone async function.
- **`textResult` helper** (TypeScript): wraps return values into the MCP text content format (`{ content: [{ type: "text", text: JSON.stringify(...) }] }`). The Python SDK handles this automatically.
- **OpenAPI route mapping** (Python OpenAPI): `custom_route_mapper` classifies GET endpoints as resources/resource-templates and non-GET as tools (only if `ENABLE_TOOLS` is set, otherwise excluded).

## Adding new tools

When adding a new MCP tool to the Python custom server:

1. Check if the generated REST client already has the endpoint function under `teamscale-rest-api-client/teamscale_rest_api_client/api/`. If not, regenerate with `./generate-client.sh`.
2. Add the import at the top of `server.py`, aliased to avoid name collisions (e.g. `from ... import get_finding as api_get_finding`).
3. Add the tool function following the `@MCP.tool()` + `@teamscale_tool` pattern with `server`/`user`/`access_key`/`fetch` params.
4. Verify with `uv run python -c "import server; print('OK')"`.
5. When calling generated client functions, convert `None` to `UNSET` for optional params.
6. Use `response.parsed.to_dict()` to return structured data, or `response.parsed` for primitives.

## Adding new skills

Skills are Markdown files at `plugins/teamscale-skills/skills/<name>/Skill.md` with YAML frontmatter (`name` and `description`). They instruct Claude Code step-by-step and reference MCP tools by their function name. See existing skills for the pattern.

## Teamscale API conventions

- **Commit descriptors**: format `branch:HEAD` or `branch:timestamp`. Used by finding-churn and test-gap endpoints.
- **Merge request identifier**: format `connectorId/mrNumber`, from `mergeRequest.identifier.idWithRepository`.
- **Test gap treemap**: requires `baseline=sourceBranch:HEAD`, `end=targetBranch:HEAD` (counterintuitive — baseline is the feature branch), plus `merge_request_mode=True`, `exclude_unchanged_methods=True`, `auto_select_branch=False`.
- **Project detection**: `get_project_id` matches by comparing `git remote get-url origin` against connector URLs. Supports GitHub, GitLab, and Stash/Bitbucket connector types.
