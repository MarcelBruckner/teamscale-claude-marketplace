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
