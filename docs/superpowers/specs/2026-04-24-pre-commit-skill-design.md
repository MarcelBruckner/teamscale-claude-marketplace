# Pre-Commit Skill Design

## Overview

A Claude Code skill (`/teamscale-skills:pre-commit`) that collects local git changes, uploads them to Teamscale's pre-commit analysis API, and presents the findings to the user as a structured summary.

## MCP Tools

Three new tools in `plugins/teamscale-python-custom/server/server.py`, all following the existing `@MCP.tool()` + `@teamscale_tool` decorator pattern.

### `pre_commit_upload`

Uploads file changes to Teamscale and returns the immediate result.

- Calls PUT `/api/projects/{project}/pre-commit3` with a JSON body mapping file paths to contents (`null` for deletions).
- Returns `PreCommit3Result`: immediate findings, optional polling token, and any errors.
- Uses `expect_body=False` in `fetch()` and manually parses the response via `PreCommit3Result.from_dict(json.loads(response.content))` to work around the generated client returning `None` for status 200.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project` | `str` | yes | Teamscale project ID |
| `changes` | `str` | yes | JSON string mapping file paths to contents (`null` for deletions) |
| `branch` | `str` | no | Repository branch the changes are based on |
| `server` | `str` | no | Teamscale URL (falls back to env) |
| `user` | `str` | no | Teamscale user (falls back to env) |
| `access_key` | `str` | no | Teamscale access key (falls back to env) |

**Returns:** Dict with `findings` (list), `token` (string or absent), `detailedErrors` (list).

### `pre_commit_poll`

Polls for pre-commit analysis results.

- Calls GET `/api/projects/{project}/pre-commit3/{token}`.
- Analysis is complete when the returned `token` field is empty or absent.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project` | `str` | yes | Teamscale project ID |
| `token` | `str` | yes | Polling token from the upload response |
| `server` | `str` | no | Teamscale URL (falls back to env) |
| `user` | `str` | no | Teamscale user (falls back to env) |
| `access_key` | `str` | no | Teamscale access key (falls back to env) |

**Returns:** Dict with `findings` (list), `token` (string or absent), `detailedErrors` (list).

### `pre_commit_analyze`

Combined tool: uploads changes, polls until analysis is complete, returns the final findings.

- Calls `pre_commit_upload` internally, then loops calling `pre_commit_poll` with `asyncio.sleep(2)` between attempts until the token is empty.
- Returns the final complete result.

**Parameters:** Same as `pre_commit_upload`.

**Returns:** Dict with `findings` (list) and `detailedErrors` (list). No token (analysis is complete).

## Skill

`plugins/teamscale-skills/skills/pre-commit/Skill.md`

A markdown document instructing Claude to execute these steps:

1. **Verify git repo** -- run `git rev-parse --is-inside-work-tree`. Abort if not in a repo.
2. **Get changed files** -- run `git diff HEAD` to get all uncommitted changes (staged + unstaged). If no changes, inform user and stop.
3. **Read file contents** -- for each changed file, read its current content. For deleted files, use `null`.
4. **Detect Teamscale project** -- call the `get_project_id` MCP tool using the repo's remote URL. If multiple projects match, use the first one.
5. **Detect branch** -- run `git branch --show-current`.
6. **Run pre-commit analysis** -- call `pre_commit_analyze` with the project, branch, and file changes map.
7. **Present findings** as a structured summary:
   - Summary header: total finding count, counts grouped by assessment/severity
   - Counts by category/group
   - Per-file detail: file path, then each finding with message, category, line location, and assessment

## Data Flow

```
User invokes /teamscale-skills:pre-commit
  |
  +-- git rev-parse --is-inside-work-tree  ->  abort if not a repo
  +-- git diff HEAD                        ->  list of changed/deleted files
  +-- Read each changed file's content     ->  { path: content } map
  +-- git remote get-url origin            ->  repo URL
  +-- get_project_id(repo_url)             ->  Teamscale project ID
  +-- git branch --show-current            ->  branch name
  |
  +-- pre_commit_analyze(project, branch, changes)
  |     |
  |     +-- PUT /api/projects/{project}/pre-commit3  ->  initial findings + token
  |     +-- loop: GET .../pre-commit3/{token}        ->  poll until token is empty
  |           +-- sleep 2s between polls
  |
  +-- Format and present findings
        +-- Summary: total count, counts by severity
        +-- Counts by category/group
        +-- Per-file: path -> findings with message, category, line, assessment
```

## Known Issues

The generated client's `request_pre_commit_analysis.py` has a `_parse_response` that returns `None` for HTTP 200 instead of parsing the `PreCommit3Result` body. The `pre_commit_upload` and `pre_commit_analyze` tools work around this by using `expect_body=False` and manually parsing with `json.loads(response.content)`.
