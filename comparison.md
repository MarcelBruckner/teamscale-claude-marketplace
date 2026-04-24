---
marp: true
theme: default
paginate: true
backgroundColor: #fff
style: |
  section {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
  section.lead h1 {
    font-size: 2.4em;
  }
  section.lead h2 {
    font-weight: 400;
    color: #555;
  }
  table {
    font-size: 0.75em;
  }
  .columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5em;
  }
  .pro { color: #2e7d32; }
  .con { color: #c62828; }
  strong { color: #1a1a1a; }
  h1 { color: #1a1a1a; }
  h2 { color: #333; }
  code { font-size: 0.85em; }
  footer {
    font-size: 0.6em;
    color: #999;
  }
---

<!-- _class: lead -->

# Teamscale + Claude Code

## From API Tools to Developer Workflows

Marcel Bruckner

---

# What We Built

We connected Teamscale to Claude Code so developers can run findings analysis, fix code quality issues, and close test gaps — all from the command line.

The stack has two layers:

1. **MCP Server** — exposes Teamscale REST API endpoints as tools Claude can call
2. **Skills** — multi-step workflows that orchestrate those tools into things developers actually want to do

We built three MCP server implementations to compare approaches, and five skills that demonstrate the real value.

---

# 🔌 MCP in 30 Seconds

The **Model Context Protocol** connects AI assistants to external tools and data.

An MCP server exposes:
- **Tools** — actions Claude can invoke (e.g. "list projects", "get findings")
- **Resources** — data Claude can read (read-only endpoints)

Claude Code has native MCP support via its **plugin system**.

We built three plugins that bridge Claude Code to the Teamscale REST API — each with a different approach.

---

# 🗺️ Three MCP Server Approaches

| | Python OpenAPI | Python Custom | TypeScript Custom |
|---|---|---|---|
| **Strategy** | Auto-generate from spec | Hand-craft curated tools | Hand-craft curated tools |
| **API coverage** | Full (121 endpoints) | ~20 selected tools | 13 selected tools |
| **Server code** | 65 lines | ~700 lines | 535 lines |
| **Runtime** | Python + uv | Python + uv | Node.js 18+ |
| **Zero-config** | ❌ Env vars required | ✅ | ✅ |

---

# Python OpenAPI — Full Auto

Fetches the OpenAPI spec from a running Teamscale instance, auto-registers all 121 endpoints.

<div class="columns">
<div>

### ✅ Advantages

- Near-zero maintenance
- New endpoints appear automatically
- Only 65 lines of code

</div>
<div>

### ⚠️ Problems

- 121 tools flood Claude's context
- Claude often picks wrong endpoint
- No higher-level business logic
- Env vars required at startup

</div>
</div>

---

# Custom Plugins — Curated Tools

Both use a generated REST client from the bundled `teamscale-openapi.json`. Hand-written tools with business logic, uniform error handling, and optional connection params.

<div class="columns">
<div>

### ✅ Advantages

- Claude picks the right tool reliably
- Higher-level logic (aggregation, verification)
- Zero-config install
- Uniform error handling

</div>
<div>

### ⚠️ Limitations

- Each new endpoint requires manual work
- Python version uses Python 3.14+

</div>
</div>

The Python and TypeScript versions expose identical tools — choose based on your runtime.

---

# Quick Comparison

| Dimension | Python OpenAPI | Python Custom | TS Custom |
|---|---|---|---|
| **Endpoints** | 121 | ~20 | 13 |
| **Zero-config install** | ❌ | ✅ | ✅ |
| **Auto new endpoints** | ✅ | ❌ | ❌ |
| **Business logic** | ❌ | ✅ | ✅ |
| **Claude picks correctly** | Unreliable | Reliable | Reliable |

**Verdict:** The auto-generated approach sounds appealing but fails in practice. Claude works much better with a small, curated tool set.

---

<!-- _class: lead -->

# 🛠️ What You Can Do With This

## Skills Turn Tools Into Workflows

---

# Skills Are the Point

MCP tools alone are building blocks. The real value comes from **skills** — multi-step workflows that orchestrate tools, read code, edit files, and guide the user.

Without skills, the user must know which tools exist, in what order to call them, and how to interpret raw API results.

With skills, the user just says what they want to accomplish.

```
/teamscale-skills:pre-commit                # "check my changes"
/teamscale-skills:merge-request-findings    # "what did my MR break?"
/teamscale-skills:fix-findings              # "fix them"
```

---

# The Five Skills

| Skill | What It Does |
|-------|-------------|
| **pre-commit** | Run Teamscale pre-commit analysis on uncommitted changes. Shows findings by file. |
| **merge-request-findings** | Auto-detect the MR for the current branch, fetch finding churn (added + in changed code). |
| **fix-findings** | Walk through findings one by one, propose code fixes, apply with confirmation. |
| **merge-request-test-gaps** | Show which changed methods in your MR lack test coverage. |
| **close-test-gaps** | For new methods: propose and write tests. For modified methods: suggest which tests to re-run. |

---

# A Typical Developer Workflow

```
/teamscale-skills:pre-commit              # 1. Run pre-commit analysis
/teamscale-skills:fix-findings            # 2. Fix the findings
/teamscale-skills:merge-request-findings  # 3. See MR findings
/teamscale-skills:fix-findings            # 4. Fix them too
/teamscale-skills:merge-request-test-gaps # 5. Check test gaps
/teamscale-skills:close-test-gaps         # 6. Write tests / re-run
```

Each skill auto-detects the project and MR from the git repo. Later skills pick up context from earlier ones.

---

# How Skills Work

A skill is a Markdown file with YAML frontmatter. No code — just step-by-step instructions:

```markdown
---
name: merge-request-findings
description: Fetch Teamscale findings for the MR on the current branch
---
### 1. Verify git repository
Run `git rev-parse --is-inside-work-tree` via Bash. ...
### 2. Detect Teamscale project
Run `git remote get-url origin`. Call `get_project_id` MCP tool. ...
### 3. Detect merge request
Call `list_merge_requests` with status OPEN. Match by branch. ...
```

Skills orchestrate MCP tools, Bash commands, and file operations into coherent workflows.

---

# Skill-Driven Development

The skills dictate which MCP tools to build — not the other way around.

```
User use case  →  Design skill  →  Implement MCP tools skill needs
```

We started from developer workflows:
- "Check my changes before pushing" → pre-commit skill → `pre_commit_analyze` tool
- "What findings does my MR have?" → merge-request-findings skill → `list_merge_requests` + `get_merge_request_finding_churn` tools
- "Close my test gaps" → close-test-gaps skill → `get_test_gap_treemap` + `get_merge_request_test_suggestions` tools

**The MCP tools exist to serve the skills.**

---

<!-- _class: lead -->

# 🔍 Observations

---

# LLM-Driven Pre-Commit Has Limits

The pre-commit skill sends file contents through the LLM as MCP tool parameters. This hits payload size limits — Claude silently strips comments/constants to fit, producing **false findings**.

A server-side approach (like `teamscale-dev`) reads files directly from disk with no size limits or content mangling. The LLM makes one tool call and gets clean results.

**Takeaway:** MCP tools that do heavy lifting in the server process are more reliable than exposing low-level building blocks for the LLM to orchestrate.

---

# Generated REST Clients Break on Version Mismatches

The generated typed clients (from `openapi-python-client` / `@hey-api/openapi-ts`) are strict — when Teamscale's API changes a field name or type, the client throws validation errors.

This makes the plugin fragile. Any Teamscale update that changes response shapes breaks tools even if the endpoint still works fine.

**Alternatives:**
- Ship the MCP server with `teamscale-dev` (stays in sync automatically)
- Skip the generated client, use plain HTTP calls with the OpenAPI spec as reference

---

# Skills Are What Make MCP Servers Useful

MCP tools alone are building blocks — they expose capabilities but don't encode **when** or **how** to use them.

Today: the user must know what to ask for.

```
User: "Check if there are architecture violations in project X"
       → Claude calls verify_architecture tool
       → Returns results

User: "..." (silence — Claude won't proactively do anything)
```

Skills turn this into:

```
User: /teamscale-skills:pre-commit
       → Skill detects project, reads changes, runs analysis,
         formats results, suggests fixes
```

---

<!-- _class: lead -->

# 🔮 Future Work

---

# Safer Authentication

| Method | ⚠️ Risk |
|---|---|
| **Env vars** | Credentials in shell history / profile |
| **In-prompt** | **Credentials sent to the LLM** as tool parameters |

**Possible improvements:**
- 🔑 **OAuth / SSO** — browser-based login, token stored locally, never sent to LLM
- 🗝️ **System keychain** — read from OS keychain
- 📄 **Local config file** — `.teamscale.json` read server-side, not exposed as params

---

# More Plugin Layers

We built MCP tools and skills. A Claude Code plugin can ship more:

| Component | What It Does | Teamscale Example |
|---|---|---|
| ✅ **MCP Server** | API tools Claude can call | `get_findings_list`, `verify_architecture` |
| ✅ **Skills** | Multi-step workflows via `/slash` commands | `/pre-commit`, `/fix-findings` |
| **Agents** | Custom personas with own system prompt | A "Teamscale QA" agent |
| **Hooks** | Auto-run on Claude Code events | Architecture check on every commit |
| **Monitors** | Background watchers | Watch worker logs for fatals |

**Next:** Collect user use cases → design skills → implement tools those skills need.

---

# Hosting Options

| | Standalone Plugin | teamscale-dev | Standalone Server | Integrated in Teamscale |
|---|---|---|---|---|
| **Local install** | Yes | Already installed | No | No |
| **Up-to-date** | User updates | With teamscale-dev | OPS updates | With Teamscale updates |
| **API version sync** | Manual | Automatic | Manual | Automatic |
| **Auth solved** | ❌ | ✅ | ❌ | ✅ |

---

<!-- _class: lead -->

# Why teamscale-dev Is the Right Choice

---

# teamscale-dev Solves the Hard Problems

The standalone plugins we built demonstrate the value, but they have structural issues that `teamscale-dev` solves by design:

| Problem | Standalone Plugin | teamscale-dev |
|---|---|---|
| **API version drift** | Bundled spec goes stale | Stays in sync automatically |
| **Pre-commit payload limits** | LLM mangling, false findings | Server-side file reading, no limits |
| **Authentication** | Env vars or in-prompt (insecure) | Already manages credentials |
| **Installation** | Separate plugin install | Already on the developer's machine |
| **Maintenance** | Separate repo, manual updates | Ships with Teamscale |

---

# What teamscale-dev Should Ship

The MCP server in `teamscale-dev` should include:

1. **The curated MCP tools** we proved out in the custom plugins — not auto-generated, not exhaustive, just the tools that skills need
2. **The skills** as a bundled plugin — these are the user-facing value and work independently of the MCP server implementation
3. **Server-side heavy lifting** — pre-commit analysis, file reading, polling should happen in the MCP server process, not through LLM tool-call chains

The standalone plugins in this marketplace are the **prototype**. `teamscale-dev` is the **production home**.

---

<!-- _class: lead -->

# 💬 Questions?
