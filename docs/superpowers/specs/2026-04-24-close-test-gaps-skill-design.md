# Close Test Gaps Skill — Design Spec

**Date:** 2026-04-24

## Overview

A new Claude Code skill (`close-test-gaps`) that proposes and applies tests for untested methods identified by Teamscale's test gap analysis. Follows the same interactive loop pattern as `fix-findings`. No new MCP tools needed — reuses existing `get_test_gap_treemap` and built-in Read/Edit tools.

## Scope

1. A new skill file at `plugins/teamscale-skills/skills/close-test-gaps/Skill.md`
2. No new MCP tools required

## Skill Flow

### Step 1: Verify git repository
Run `git rev-parse --is-inside-work-tree`. Stop with error message if not a repo.

### Step 2: Detect Teamscale project
Run `git remote get-url origin` to get the repo URL. Call `get_project_id` MCP tool. If multiple projects returned, ask user. If none or error, stop with message.

### Step 3: Determine test gaps to close

Check the conversation context for untested methods from a prior `merge-request-test-gaps` skill run.

**If test gap data exists in context:** Present the untested methods (UNTESTED_CHANGE and UNTESTED_ADDITION) as a numbered list showing for each:
- File path (from `uniformPath`)
- Method name (from `methodName`)
- State (UNTESTED_CHANGE or UNTESTED_ADDITION)

Ask the user: "Would you like to close these test gaps, or provide a specific method instead?"
- If the user wants to close these, use the methods from context.
- If the user wants a specific method, ask for a file path and method name.

**If no test gap data in context:** Run the same flow as `merge-request-test-gaps` steps 3-5:
1. Detect the MR (branch matching or user selection)
2. Select partitions (default all)
3. Fetch treemap via `get_test_gap_treemap`
4. Extract methods with state UNTESTED_CHANGE or UNTESTED_ADDITION

If no untested methods are found, tell the user: "No test gaps detected — all changed methods have test coverage." Then stop.

### Step 4: Test gap loop

For each untested method:

**4a. Read the source method**

Using `uniformPath` from the method node, read the relevant source file with the Read tool. Focus on the area around the method (use `methodName` and line info from `start`/`end` fields if available).

**4b. Detect test conventions**

Look for existing test files near the source file:
- Search for files matching patterns like `*Test*`, `*Spec*`, `test_*` in the same directory or adjacent `test/`/`tests/` directories
- Read one or two existing test files to detect: test framework (JUnit, pytest, Jest, etc.), naming conventions, import patterns, assertion style

**4c. Propose a test**

Based on the source method and detected test conventions, propose a test. Show the user:
1. A brief explanation of what the method does
2. The proposed test code (matching the project's test framework and style)
3. Which file the test should be added to (existing test file or new one)

**4d. Ask for confirmation**

Ask the user: "Apply this test? (yes / skip / stop)"

- **yes:** Write or edit the test file using the Write or Edit tool. Tell the user the test was added. Continue to the next method.
- **skip:** Tell the user this method was skipped. Continue to the next method.
- **stop:** End the loop immediately. Go to step 5.

### Step 5: Wrap up

Present a summary:
- Number of test gaps closed
- Number skipped
- Number remaining (if stopped early)

Offer to re-run: "Would you like to re-run test gap analysis to verify? (yes / no)"

- **yes:** Invoke the `merge-request-test-gaps` skill.
- **no:** Done.

## Design Decisions

- **No new MCP tools** — the existing `get_test_gap_treemap` provides all method-level data needed. The skill uses built-in Read/Edit tools for code manipulation.
- **Context integration** — primary workflow is: run `merge-request-test-gaps` → see gaps → close them. Avoids re-fetching.
- **Detect test conventions** — reads nearby test files to match framework, naming, and style rather than guessing.
- **Per-method confirmation** — same interactive pattern as `fix-findings`. User stays in control.
- **Re-run offered at end** — one verification pass, not per-method.
