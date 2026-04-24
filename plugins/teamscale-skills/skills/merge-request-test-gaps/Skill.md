---
name: merge-request-test-gaps
description: Show Teamscale test gap analysis for the merge request on the current branch
---

# Teamscale Merge Request Test Gaps

Show which methods changed in the current merge request lack test coverage, using Teamscale's test gap analysis.

## Steps

### 1. Verify git repository

Run `git rev-parse --is-inside-work-tree` via Bash.

If this fails, tell the user: "This directory is not inside a git repository. Please navigate to a git repository and try again." Then stop.

### 2. Detect Teamscale project

Run `git remote get-url origin` via Bash to get the repository URL.

Call the `get_project_id` MCP tool with this URL.

If multiple projects are returned, ask the user which project to use. If one project is returned, use it. If the tool errors, tell the user and stop.

### 3. Detect merge request

Check the conversation context for an already-identified merge request (from a prior `merge-request-findings` run). If found, reuse it and tell the user which MR is being used.

If no MR in context, run the standard detection flow:

1. Run `git branch --show-current` via Bash to get the current branch name.
2. Call the `list_merge_requests` MCP tool with `project` and `status` set to `"OPEN"`.
3. From the returned list, find merge requests whose `mergeRequest.sourceBranch` equals the current branch name.

**Exactly one match:** Use it. Tell the user which MR was found: its title and source branch -> target branch.

**No match but list is non-empty:** Show the full list of open MRs (title, source branch -> target branch for each) and ask the user to pick one.

**No open MRs at all:** Tell the user: "No open merge requests found for this project." Then stop.

**Multiple matches:** Show the matching MRs (title, source branch -> target branch for each) and ask the user to pick one.

### 4. Select partitions

Call the `get_test_gap_partitions` MCP tool with `project`.

If partitions are returned, show them to the user and ask: "Use all partitions, or select specific ones? (default: all)"

- If the user wants all (or just confirms the default), use `all_partitions=true` for subsequent calls.
- If the user selects specific partitions, use `all_partitions=false` and pass the selected names as `partitions`.

If no partitions are returned, tell the user: "No test coverage partitions found for this project. Test gap analysis requires test coverage data." Then stop.

### 5. Fetch test gap data

Using the selected merge request's `mergeRequest.sourceBranch` and `mergeRequest.targetBranch`, construct commit descriptors:
- `end`: `"{sourceBranch}:HEAD"`
- `baseline`: `"{targetBranch}:HEAD"`

Call both MCP tools with the project, end, baseline, and partition config:
- `get_test_gap_percentage`
- `get_test_gap_treemap`

### 6. Present results

**Summary header:**
- Test gap percentage (from the percentage result, formatted as a percentage like "73% tested")
- State counts from `stateCounter.map` in the treemap result:
  - TESTED_CHURN: methods changed and tested
  - UNTESTED_CHANGE: methods changed but not tested
  - UNTESTED_ADDITION: new methods without tests
  - UNCHANGED: methods not changed (for context)

**Per-file detail:**
- The treemap result contains a tree of `TgaMethodTreeMapNode` objects. Walk the tree recursively via `children` to find leaf nodes (methods).
- Group method nodes by file path (extract file path from `uniformPath` by removing the method part).
- For each file that has methods with state UNTESTED_CHANGE or UNTESTED_ADDITION:
  - Show the file path as a heading
  - For each untested method in that file, show: `methodName` and `state` (UNTESTED_CHANGE or UNTESTED_ADDITION)
- Skip files where all methods are tested or unchanged.

**Empty state:** If there are no methods with UNTESTED_CHANGE or UNTESTED_ADDITION, tell the user: "No test gaps detected for this merge request — all changed methods have test coverage."
