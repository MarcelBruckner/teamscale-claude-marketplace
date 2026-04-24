# Teamscale Skills Plugin

Claude Code skills that orchestrate Teamscale MCP tools into multi-step workflows. Each skill is a Markdown file with YAML frontmatter that instructs Claude Code how to perform a task.

## Skills

### pre-commit
Run Teamscale pre-commit analysis on all uncommitted changes and present findings grouped by file with assessment, category, and message.

### merge-request-findings
Fetch and present Teamscale findings (added + in changed code) for the merge request on the current branch. Auto-detects the MR by matching the local branch to open MRs.

### fix-findings
Propose and apply code fixes for Teamscale findings one at a time with user confirmation. Integrates with prior `pre-commit` or `merge-request-findings` runs, or accepts a finding ID / file+line manually.

### merge-request-test-gaps
Show Teamscale test gap analysis for the current MR. Displays which changed methods lack test coverage, with a summary ratio and per-file detail of untested methods.

### close-test-gaps
Close test gaps identified by `merge-request-test-gaps`. For new methods (UNTESTED_ADDITION), proposes and writes tests matching the project's test framework. For modified methods (UNTESTED_CHANGE), fetches Teamscale's impacted test suggestions.

## Installation

```
/plugins marketplace add ./
/plugins install teamscale-skills
/reload-plugins
```

## Requirements

Requires the `teamscale-python-custom` (or `teamscale-typescript-custom`) MCP server plugin to be installed and configured, as all skills call Teamscale MCP tools.
