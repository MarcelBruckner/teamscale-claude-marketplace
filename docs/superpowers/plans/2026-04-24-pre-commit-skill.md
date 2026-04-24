# Pre-Commit Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `/teamscale-skills:pre-commit` skill that collects local git changes, uploads them to Teamscale's pre-commit3 API, and presents findings as a structured summary.

**Architecture:** Three new MCP tools in the Python custom plugin (`pre_commit_upload`, `pre_commit_poll`, `pre_commit_analyze`) use the existing generated REST client. A Skill.md file orchestrates git commands and tool calls to drive the workflow.

**Tech Stack:** Python 3.14+, FastMCP, generated `teamscale_rest_api_client`, Claude Code skills (Markdown)

---

## File Structure

| Action | Path | Responsibility |
|--------|------|---------------|
| Modify | `plugins/teamscale-python-custom/server/server.py:1-19` | Add imports for pre-commit API functions and models |
| Modify | `plugins/teamscale-python-custom/server/server.py:407+` | Add three new tool functions before `main()` |
| Create | `plugins/teamscale-skills/skills/pre-commit/Skill.md` | Skill orchestration instructions |
| Modify | `.claude-plugin/marketplace.json` | Register the skills plugin |

---

### Task 1: Add `pre_commit_upload` tool

**Files:**
- Modify: `plugins/teamscale-python-custom/server/server.py:1-19` (imports)
- Modify: `plugins/teamscale-python-custom/server/server.py:432` (before `main()`)

- [ ] **Step 1: Add imports**

Add these imports to the top of `server.py`, after the existing import block (line 19):

```python
import json

from teamscale_rest_api_client.api.pre_commit import request_pre_commit_analysis, poll_pre_commit_results
from teamscale_rest_api_client.models.request_pre_commit_analysis_body import RequestPreCommitAnalysisBody
from teamscale_rest_api_client.models.pre_commit_3_result import PreCommit3Result
```

- [ ] **Step 2: Add the `pre_commit_upload` tool**

Insert before the `main()` function (currently at line 435):

```python
@MCP.tool()
@teamscale_tool
async def pre_commit_upload(
    project: str,
    changes: str,
    branch: str | None = None,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> dict:
    """Upload file changes for pre-commit analysis and return immediate results.

    The changes parameter is a JSON string mapping file paths to their new content.
    Use null values for deleted files. Example: {"src/foo.py": "print('hi')", "old.py": null}
    Returns findings, an optional polling token, and any errors.
    """
    client = resolve_connection(server, user, access_key)
    body = RequestPreCommitAnalysisBody()
    body.additional_properties = json.loads(changes)
    response = await fetch(
        request_pre_commit_analysis.asyncio_detailed(
            project=project,
            client=client,
            body=body,
            branch=branch if branch is not None else UNSET,
        ),
        expect_body=False,
    )
    result = PreCommit3Result.from_dict(json.loads(response.content))
    return result.to_dict()
```

- [ ] **Step 3: Verify the server still starts**

Run:
```bash
cd plugins/teamscale-python-custom/server && uv run python -c "import server; print('OK')"
```

Expected: `OK` (no import errors)

- [ ] **Step 4: Commit**

```bash
git add plugins/teamscale-python-custom/server/server.py
git commit -m "feat: add pre_commit_upload MCP tool"
```

---

### Task 2: Add `pre_commit_poll` tool

**Files:**
- Modify: `plugins/teamscale-python-custom/server/server.py` (after `pre_commit_upload`)

- [ ] **Step 1: Add the `pre_commit_poll` tool**

Insert after `pre_commit_upload`:

```python
@MCP.tool()
@teamscale_tool
async def pre_commit_poll(
    project: str,
    token: str,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> dict:
    """Poll for pre-commit analysis results using a token from pre_commit_upload.

    Analysis is complete when the returned token field is absent or empty.
    """
    client = resolve_connection(server, user, access_key)
    response = await fetch(
        poll_pre_commit_results.asyncio_detailed(
            project=project,
            token=token,
            client=client,
        ),
    )
    return response.parsed.to_dict()
```

- [ ] **Step 2: Verify the server still starts**

Run:
```bash
cd plugins/teamscale-python-custom/server && uv run python -c "import server; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add plugins/teamscale-python-custom/server/server.py
git commit -m "feat: add pre_commit_poll MCP tool"
```

---

### Task 3: Add `pre_commit_analyze` tool

**Files:**
- Modify: `plugins/teamscale-python-custom/server/server.py` (after `pre_commit_poll`)

- [ ] **Step 1: Add the `pre_commit_analyze` tool**

Insert after `pre_commit_poll`:

```python
@MCP.tool()
@teamscale_tool
async def pre_commit_analyze(
    project: str,
    changes: str,
    branch: str | None = None,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> dict:
    """Upload file changes and poll until pre-commit analysis is complete.

    Combined tool: uploads changes, then polls every 2 seconds until analysis finishes.
    The changes parameter is a JSON string mapping file paths to their new content.
    Use null values for deleted files. Example: {"src/foo.py": "print('hi')", "old.py": null}
    Returns the final findings and any errors.
    """
    client = resolve_connection(server, user, access_key)
    body = RequestPreCommitAnalysisBody()
    body.additional_properties = json.loads(changes)
    response = await fetch(
        request_pre_commit_analysis.asyncio_detailed(
            project=project,
            client=client,
            body=body,
            branch=branch if branch is not None else UNSET,
        ),
        expect_body=False,
    )
    result = PreCommit3Result.from_dict(json.loads(response.content))

    while result.token is not UNSET and result.token:
        await asyncio.sleep(2)
        poll_response = await fetch(
            poll_pre_commit_results.asyncio_detailed(
                project=project,
                token=result.token,
                client=client,
            ),
        )
        result = poll_response.parsed

    return result.to_dict()
```

- [ ] **Step 2: Verify the server still starts**

Run:
```bash
cd plugins/teamscale-python-custom/server && uv run python -c "import server; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add plugins/teamscale-python-custom/server/server.py
git commit -m "feat: add pre_commit_analyze MCP tool"
```

---

### Task 4: Write the Skill.md

**Files:**
- Create: `plugins/teamscale-skills/skills/pre-commit/Skill.md`

- [ ] **Step 1: Write the skill file**

Write this content to `plugins/teamscale-skills/skills/pre-commit/Skill.md`:

````markdown
---
name: pre-commit
description: Run Teamscale pre-commit analysis on local git changes and present findings
---

# Teamscale Pre-Commit Analysis

Run Teamscale's pre-commit analysis on all uncommitted changes in the current repository and present the findings.

## Steps

### 1. Verify git repository

Run `git rev-parse --is-inside-work-tree` via Bash.

If this fails, tell the user: "This directory is not inside a git repository. Please navigate to a git repository and try again." Then stop.

### 2. Get changed files

Run `git diff HEAD --name-status` via Bash to get a list of all uncommitted changes (staged and unstaged) relative to HEAD.

If there are no changes, tell the user: "No uncommitted changes found." Then stop.

Parse the output. Each line has the format `STATUS\tFILE_PATH`:
- `A` or `M` or `T` = added/modified file (read its content)
- `D` = deleted file (use `null`)
- `R...` = rename (old path is deleted with `null`, new path has content)

### 3. Build the changes map

For each changed/added file from step 2, read the file's current content using the Read tool.

Build a JSON object mapping each file's path (relative to the repo root) to its content. For deleted files, map the path to `null`.

### 4. Detect Teamscale project

Run `git remote get-url origin` via Bash to get the repository URL.

Call the `get_project_id` MCP tool with this URL.

If multiple projects are returned, ask the user which project to use. If one project is returned, use it. If the tool errors, tell the user and stop.

### 5. Detect branch

Run `git branch --show-current` via Bash to get the current branch name.

### 6. Run pre-commit analysis

Call the `pre_commit_analyze` MCP tool with:
- `project`: the Teamscale project ID from step 4
- `changes`: the JSON string of the changes map from step 3
- `branch`: the branch name from step 5

Tell the user that analysis is running and may take a moment.

### 7. Present findings

Format the results as a structured summary:

**Summary header:**
- Total number of findings
- Counts grouped by assessment (RED / YELLOW / GREEN), e.g.: "RED: 3, YELLOW: 5, GREEN: 1"

**Counts by category:**
- Group findings by `categoryName`, show count per category sorted descending

**Per-file details:**
- For each file that has findings (grouped by `location.uniformPath`):
  - Show the file path as a heading
  - For each finding in that file, show:
    - Line: `location.rawStartLine` (if available)
    - Assessment: the `assessment` value
    - Category: `categoryName`
    - Message: `message`

If there are no findings, tell the user: "No findings detected in your changes."

If there are `detailedErrors` in the response, show them as warnings before the findings summary.
````

- [ ] **Step 2: Commit**

```bash
git add plugins/teamscale-skills/skills/pre-commit/Skill.md
git commit -m "feat: add pre-commit skill"
```

---

### Task 5: Register the skills plugin in marketplace.json

**Files:**
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Add the skills plugin entry**

Add this entry to the `plugins` array in `.claude-plugin/marketplace.json`, after the existing three entries:

```json
{
  "name": "teamscale-skills",
  "source": "./plugins/teamscale-skills",
  "description": "Skills for Claude to work with Teamscale."
}
```

- [ ] **Step 2: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "feat: register teamscale-skills plugin in marketplace"
```
