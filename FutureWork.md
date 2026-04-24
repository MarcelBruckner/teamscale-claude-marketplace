# Future Work

## Safer Authentication

Today, credentials are either passed as environment variables (risk: shell history / profile exposure) or as tool parameters in the prompt (risk: credentials become part of the conversation context sent to Anthropic's API).

Both approaches are problematic. Possible improvements:
- **OAuth / SSO** -- browser-based login, token stored locally, never sent to the LLM
- **System keychain** -- read from OS keychain (macOS Keychain, etc.)
- **Local config file** -- `.teamscale.json` read by the MCP server, not exposed as tool parameters

## teamscale-dev as the Natural Home for the MCP Server

`teamscale-dev` already runs locally alongside the developer's IDE and stays in sync with the Teamscale version. Its built-in MCP server is the most appropriate place to host Teamscale's MCP tools -- it solves the API version mismatch problem (see Observations), handles heavy lifting like pre-commit analysis server-side, and doesn't require a separate plugin install or maintenance. Rather than maintaining standalone MCP server plugins, investing in `teamscale-dev`'s built-in server is the most sustainable path forward.

## Hosting Options

Currently the MCP server runs locally on the developer's machine. Alternative deployment models:

| | Standalone Plugin | teamscale-dev (built-in) | Standalone Server | Integrated in Teamscale |
|---|---|---|---|---|
| **Local install needed** | Yes | Already installed | No | No |
| **Always up-to-date** | User updates | With teamscale-dev updates | OPS updates | With every Teamscale update |
| **Teamscale changes needed** | None | None (ships with it) | None (external tool) | Yes (built-in) |
| **API version sync** | Manual (spec bundled) | Automatic | Manual | Automatic |
| **Authentication** | Env vars or in-prompt (insecure) | Already handled | Open problem | Already handled |

`teamscale-dev` is the sweet spot -- no extra install, no version drift, no separate maintenance, and authentication is already solved since `teamscale-dev` manages credentials independently of the LLM.

## From Tools to Workflows

MCP gives Claude the **ability** to talk to Teamscale -- but not the **initiative**. The MCP server is the foundation, not the solution. Skills are the most important layer on top: they turn low-level API tools into concrete workflows that users can invoke without knowing the underlying tools.

We already built five skills that demonstrate this:
- `/pre-commit` -- run Teamscale pre-commit analysis on local changes
- `/merge-request-findings` -- fetch findings for the merge request on the current branch
- `/merge-request-test-gaps` -- identify test gaps for the current merge request
- `/fix-findings` -- propose and apply fixes for Teamscale findings
- `/close-test-gaps` -- write tests to close test gaps identified by Teamscale

These skills orchestrate multiple MCP tool calls, handle polling, format results, and guide the user through the workflow. Without them, the user would have to know which tools to call, in what order, and how to interpret raw API responses.

A Claude Code plugin can ship additional layers beyond skills:

| Component | What It Does | Teamscale Example |
|---|---|---|
| **MCP Server** (done) | API tools Claude can call | `get_findings_list`, `verify_architecture` |
| **Skills** (done, most important) | Multi-step workflows invoked via `/slash` commands | `/pre-commit`, `/fix-findings` |
| **Agents** | Custom personas with own system prompt & tool set | A "Teamscale QA" agent focused on code quality |
| **Hooks** | Auto-run on Claude Code events (file edit, commit, ...) | Check architecture compliance on every commit |
| **Monitors** | Background watchers that stream events to Claude | Watch Teamscale worker logs for fatals in real-time |

Next steps: collect more user use cases to drive new skills. The use cases define the skills, and the skills dictate which MCP tools to build or extend (see Observations).
