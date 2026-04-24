---
name: close-test-gaps
description: Propose and apply tests for untested methods from Teamscale test gap analysis
---

# Close Teamscale Test Gaps

Propose and apply tests for methods that lack test coverage, one at a time, with user confirmation before each change.

## Steps

### 1. Verify git repository

Run `git rev-parse --is-inside-work-tree` via Bash.

If this fails, tell the user: "This directory is not inside a git repository. Please navigate to a git repository and try again." Then stop.

### 2. Detect Teamscale project

Run `git remote get-url origin` via Bash to get the repository URL.

Call the `get_project_id` MCP tool with this URL.

If multiple projects are returned, ask the user which project to use. If one project is returned, use it. If the tool errors, tell the user and stop.

### 3. Determine test gaps to close

Check the conversation context for untested methods from a prior `merge-request-test-gaps` skill run.

**If test gap data exists in context:** Present the untested methods (those with state UNTESTED_CHANGE or UNTESTED_ADDITION) as a numbered list showing for each:
- File path (from `uniformPath`)
- Method name (from `methodName`)
- State (UNTESTED_CHANGE or UNTESTED_ADDITION)

Ask the user: "Would you like to close these test gaps, or provide a specific method instead?"
- If the user wants to close these, use the methods from context.
- If the user wants a specific method, ask for a file path and method name.

**If no test gap data in context:** Run the same flow as the `merge-request-test-gaps` skill steps 3-5:
1. Detect the MR (check context for an already-identified MR, or detect via `git branch --show-current` + `list_merge_requests` with status OPEN, matching by `mergeRequest.sourceBranch`).
2. Select partitions (call `get_test_gap_partitions`, ask user, default to all).
3. Fetch treemap via `get_test_gap_treemap` with `baseline` = `"{sourceBranch}:HEAD"`, `end` = `"{targetBranch}:HEAD"`, and `merge_request_identifier` from `mergeRequest.identifier.idWithRepository`.
4. Extract methods with state UNTESTED_CHANGE or UNTESTED_ADDITION from the treemap by walking the tree recursively via `children`.

If no untested methods are found, tell the user: "No test gaps detected — all changed methods have test coverage." Then stop.

### 4. Test gap loop

For each untested method:

**4a. Read the source method**

Using `uniformPath` from the method node, read the relevant source file with the Read tool. Focus on the area around the method (use `methodName` and the `start`/`end` line fields if available to locate it).

**4b. Detect test conventions**

Look for existing test files near the source file:
- Search for files matching patterns like `*Test*`, `*Spec*`, `test_*` in the same directory or adjacent `test/`/`tests/` directories using the Glob tool.
- Read one or two existing test files to detect: test framework (JUnit, pytest, Jest, etc.), naming conventions, import patterns, assertion style.

**4c. Handle based on state**

The action depends on the method's test gap state:

**UNTESTED_ADDITION** (new method without any tests):

This method needs a new test. Based on the source method and detected test conventions, propose a test. Show the user:
1. A brief explanation of what the method does
2. The proposed test code (matching the project's test framework and style)
3. Which file the test should be added to (existing test file or new one)

Ask the user: "Apply this test? (yes / skip / stop)"
- **yes:** Write or edit the test file using the Write or Edit tool. Tell the user the test was added. Continue to the next method.
- **skip:** Skip this method. Continue to the next.
- **stop:** End the loop. Go to step 5.

**UNTESTED_CHANGE** (existing method modified but not re-tested):

This method already has tests but they haven't been run since the modification. Find the existing tests that cover this method:
1. Search for test files that reference the method name or the class it belongs to.
2. Read those test files to identify relevant test cases.

Show the user:
1. Which existing tests likely cover this method
2. The commands to run those specific tests

Ask the user: "Run these tests? (yes / skip / stop)"
- **yes:** Run the suggested test commands via Bash. Report the results. Continue to the next method.
- **skip:** Skip this method. Continue to the next.
- **stop:** End the loop. Go to step 5.

### 5. Wrap up

Present a summary:
- Number of new tests written (UNTESTED_ADDITION)
- Number of existing tests re-run (UNTESTED_CHANGE)
- Number of methods skipped
- Number of methods remaining (if stopped early)

Then ask: "Would you like to re-run test gap analysis to verify? (yes / no)"

- **yes:** Invoke the `merge-request-test-gaps` skill.
- **no:** Done.
