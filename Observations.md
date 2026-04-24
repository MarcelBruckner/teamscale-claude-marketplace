# Observations

## Pre-Commit Analysis: Tool Size Limitation causes false findings

**Context:** Claude ran the pre-commit skill on a refactored Java codebase. The refactoring had resolved 5 original findings (4 code clones + 1 long method).

**What happened:** The MCP tool has a payload size limit. To fit the changed files into the tool call, Claude silently stripped Javadoc comments and some enum constants from the file content before uploading. This caused Teamscale to report 13 findings (11 "Missing Interface Comment", 2 "Unused Code") that don't exist in the actual source files.

**Key problem:** Claude presented the results in a way that made the false positives transparent -- but only because it knew what it had stripped. A user unfamiliar with the limitation could easily mistake these for real issues and waste time investigating or "fixing" them.

**Observation:**
- The pre-commit tool needs guardrails for large payloads. Either reject files that exceed the limit with a clear error, or find a way to send full content (chunking, compression, temp file reference).
- Claude's strategy of stripping comments/constants to fit the payload is creative but dangerous -- it changes the analysis input in ways that produce misleading results.
- Despite the false positives, the analysis correctly confirmed that the 5 original findings were resolved, so the core value (validating the refactoring) was delivered.

## Server-side pre-commit (teamscale-dev) is superior to LLM-driven pre-commit

`teamscale-dev` is Teamscale's CLI tool, already installed on developer machines. It can be registered as an MCP server in Claude Code and handles the entire pre-commit workflow itself -- reading changed files from the workspace, assembling the payload, uploading to Teamscale, and polling for results. This is fundamentally better suited than having the LLM orchestrate these steps via low-level MCP tools.

**Why the LLM approach is problematic:**
- The LLM has to read file contents, which are subject to tool payload size limits (see above). It may silently truncate or modify content to fit, producing false findings.
- The LLM must figure out which files changed, read them, format the upload payload, and manage the poll loop -- all steps where it can make mistakes or take shortcuts.
- Each step is a separate tool call, adding latency and token cost.

**Why the MCP server approach is better:**
- The MCP server reads files directly from disk with no size limits or content mangling.
- The git diff, file reading, upload, and polling logic is deterministic code, not LLM improvisation.
- The LLM only needs a single tool call and gets back clean results.

**Takeaway:** MCP tools that do the heavy lifting in the server process and return structured results are much more reliable than exposing low-level building blocks and relying on the LLM to orchestrate them correctly. Both approaches are local -- the difference is whether the logic lives in deterministic code (MCP server) or in LLM tool-call chains.

## Generated REST clients break on API version mismatches

Our approach generates typed REST clients (via `openapi-python-client` / `@hey-api/openapi-ts`) from a bundled `teamscale-openapi.json` spec. When the Teamscale instance runs a different version than the spec was generated from, the response schemas no longer match, causing Zod validation errors that break tool calls entirely.

This makes the plugin fragile -- any Teamscale update that changes response shapes (new fields, renamed fields, changed types) will cause failures even if the endpoint itself still works fine.

**Alternatives:**
- `teamscale-dev` (Teamscale's CLI tool, usable as MCP server) would be more appropriate here since it's maintained alongside Teamscale and stays in sync with the API.
- A more resilient middle ground: skip the generated client entirely, give the MCP server the OpenAPI spec as reference, and have the tools make plain HTTP calls. This avoids strict schema validation on responses and tolerates minor API drift gracefully -- a missing or extra field in the response won't crash the tool.

## Skills are what makes MCP servers useful

MCP tools alone are building blocks -- they expose API capabilities but don't encode how or when to use them. The real value comes from skills that orchestrate these tools into concrete workflows (e.g. `/pre-commit`, `/merge-request-findings`, `/fix-findings`). Without skills, the user has to know which tools exist, in what order to call them, and how to interpret the results. With skills, the user just says what they want to accomplish.

This means skill-driven development should guide how we build MCP servers: the MCP tools exist to serve the skills, not the other way around. The right approach is to start from user use cases, design skills around them, and then implement whatever MCP tools those skills need.

**Implication:** We need to collect concrete use cases from users -- what workflows do they want automated with Teamscale? Those use cases become skills, and the skills dictate which MCP tools to build or extend.
