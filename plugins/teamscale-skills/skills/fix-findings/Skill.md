---
name: fix-findings
description: Fix Teamscale findings by proposing and applying code changes with user confirmation
---

# Fix Teamscale Findings

Propose and apply fixes for Teamscale findings, one at a time, with user confirmation before each change.

## Steps

### 1. Verify git repository

Run `git rev-parse --is-inside-work-tree` via Bash.

If this fails, tell the user: "This directory is not inside a git repository. Please navigate to a git repository and try again." Then stop.

### 2. Detect Teamscale project

Run `git remote get-url origin` via Bash to get the repository URL.

Call the `get_project_id` MCP tool with this URL.

If multiple projects are returned, ask the user which project to use. If one project is returned, use it. If the tool errors, tell the user and stop.

### 3. Determine findings to fix

Check the conversation context for findings from a prior `pre-commit` or `merge-request-findings` skill run.

**If findings exist in context:** Present them as a numbered list showing for each finding:
- File path (`location.uniformPath`)
- Location (`location.location`, if available)
- Category (`categoryName`)
- Message (`message`)

Ask the user: "Would you like to fix these findings, or provide a specific finding instead?"
- If the user wants to fix these, use the findings from context. Extract the `id` field from each finding.
- If the user wants to provide a specific finding, go to the manual input path below.

**If no findings in context:** Ask the user for either:
- A finding ID (string)
- A file path and line number

If the user provides a file path and line number instead of an ID, call the `get_findings_list` MCP tool with `project` and `uniform_path` set to the file path. From the results, find findings whose `location.location` contains the given line number. Present matches and let the user confirm which one(s) to fix.

### 4. Fix loop

For each finding to fix:

**4a. Fetch full finding details**

Call the `get_finding` MCP tool with:
- `project`: the Teamscale project ID from step 2
- `id`: the finding's ID

This returns the full finding with message, properties, secondary locations, and other details needed to understand the issue. If the tool errors (e.g. finding not found), tell the user and skip to the next finding.

**4b. Read the source file**

Using `location.uniformPath` from the finding, read the relevant source file with the Read tool. Focus on the area around the finding's location.

**4c. Propose a fix**

Analyze the finding's:
- `categoryName` and `message` — what the issue is
- `properties` — additional context (e.g. expected values, thresholds)
- `secondaryLocations` — related code locations that may need changes too
- The surrounding source code

Propose a concrete code fix. Show the user:
1. A brief explanation of what the finding means
2. The exact code change (before → after)

**4d. Ask for confirmation**

Ask the user: "Apply this fix? (yes / skip / stop)"

- **yes:** Apply the edit using the Edit tool. Tell the user the fix was applied. Continue to the next finding.
- **skip:** Tell the user this finding was skipped. Continue to the next finding.
- **stop:** End the fix loop immediately. Go to step 5.

### 5. Wrap up

Present a summary:
- Number of findings fixed
- Number of findings skipped
- Number of findings remaining (if stopped early)

Then ask: "Would you like to re-run analysis to verify the fixes? (pre-commit / merge-request / no)"

- **pre-commit:** Invoke the `pre-commit` skill.
- **merge-request:** Invoke the `merge-request-findings` skill.
- **no:** Done.
