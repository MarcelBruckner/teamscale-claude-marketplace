---
name: merge-request-findings
description: Fetch Teamscale findings for the merge request on the current branch
---

# Teamscale Merge Request Findings

Fetch and present Teamscale's analysis findings for the merge request associated with the current branch.

## Steps

### 1. Verify git repository

Run `git rev-parse --is-inside-work-tree` via Bash.

If this fails, tell the user: "This directory is not inside a git repository. Please navigate to a git repository and try again." Then stop.

### 2. Detect Teamscale project

Run `git remote get-url origin` via Bash to get the repository URL.

Call the `get_project_id` MCP tool with this URL.

If multiple projects are returned, ask the user which project to use. If one project is returned, use it. If the tool errors, tell the user and stop.

### 3. Detect current branch

Run `git branch --show-current` via Bash to get the current branch name.

### 4. Find the merge request

Call the `list_merge_requests` MCP tool with:
- `project`: the Teamscale project ID from step 2
- `status`: `"OPEN"`

From the returned list, find merge requests whose `mergeRequest.sourceBranch` equals the current branch name from step 3.

**Exactly one match:** Use it. Tell the user which MR was found: its title and source branch -> target branch.

**No match:** Show the full list of open MRs (title, source branch -> target branch for each) and ask the user to pick one.

**Multiple matches:** Show the matching MRs (title, source branch -> target branch for each) and ask the user to pick one.

### 5. Fetch finding churn

Using the selected merge request's `mergeRequest.sourceBranch` and `mergeRequest.targetBranch`, call the `get_merge_request_finding_churn` MCP tool with:
- `project`: the Teamscale project ID from step 2
- `source`: `"{sourceBranch}:HEAD"` (e.g. `"feature-branch:HEAD"`)
- `target`: `"{targetBranch}:HEAD"` (e.g. `"main:HEAD"`)

### 6. Present findings

Format the results as a structured summary.

**Summary header:**
- Count of added findings (from `addedFindings.findings`)
- Count of findings in changed code (from `findingsInChangedCode.findings`)
- Counts grouped by assessment (RED / YELLOW / GREEN) across both added and in-changed-code findings
- Note about removed findings: "X findings were removed by this MR." (from `removedFindings.findings` count)

**Added findings (per file):**
- Show a heading: "Added Findings"
- Group findings by `location.uniformPath`
- For each file that has findings, show the file path as a subheading
- For each finding in that file, show:
  - Line: `location.rawStartLine` (if available)
  - Assessment: the `assessment` value
  - Category: `categoryName`
  - Message: `message`

**Findings in changed code (per file):**
- Show a heading: "Findings in Changed Code"
- Same format as added findings above

If both `addedFindings.findings` and `findingsInChangedCode.findings` are empty, tell the user: "No findings detected for this merge request."
