---
marp: true
theme: default
paginate: true
backgroundColor: #fff
style: |
  section {
    font-family: Futura, 'Futura Std', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #333;
    border-left: 16px solid transparent;
    border-image: linear-gradient(to bottom, #bbb 0%, #bbb 20%, #fff 20%, #fff 35%, #E87722 35%, #E87722 100%) 1;
  }
  section.lead h1 {
    font-size: 2.4em;
    color: #333;
  }
  section.lead h2 {
    font-weight: 400;
    color: #999;
  }
  h1 {
    color: #1a1a1a;
  }
  h2 { color: #555; }
  h3 { color: #E87722; }
  table {
    font-size: 0.75em;
  }
  .columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5em;
  }
  strong { color: #1a1a1a; }
  a { color: #E87722; }
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

# OpenAPI based — Full Auto

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

Hand-written tools with business logic, uniform error handling, and optional connection params.

<div class="columns">
<div>

### ✅ Advantages

- Claude picks the right tool reliably
- Higher-level logic (aggregation, verification)
- Zero-config install

</div>
<div>

### ⚠️ Limitations

- Each new endpoint requires manual work

</div>
</div>

The Python and TypeScript versions expose identical tools.

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

# 🛠️ How To Use MCP Tools

## Skills Turn Tools Into Workflows

---

# Skills Are the Point

MCP tools alone are building blocks. The real value comes from **skills** — slash commands that orchestrate tools, read code, edit files, and guide the user through multi-step workflows.

Without skills, the user must know which tools exist, in what order to call them, and how to interpret raw API results.

With skills, the user just says what they want to accomplish.

```
/teamscale-skills:pre-commit                # "check my changes"
/teamscale-skills:merge-request-findings    # "what did my MR break?"
/teamscale-skills:fix-findings              # "fix them"
```

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

# Why Skills Matter

With only MCP tools, the user must know what to ask for:

```
User: "Check if there are architecture violations in project X"
       → Claude calls verify_architecture tool
       → Returns results
```

With skills:

```
User: /teamscale-skills:pre-commit
       → Skill detects project, reads changes, runs analysis,
         formats results, suggests fixes
```

---

<!-- _class: lead -->

# 🔍 Observations

---

# LLM-Driven Pre-Commit Has Limits

The pre-commit skill sends file contents through the LLM as MCP tool parameters. This hits payload size limits — Claude silently strips comments/constants to fit, producing **false findings**.

`teamscale-dev` handles this natively — it reads files directly from disk with no size limits or content mangling. The LLM makes one tool call and gets clean results.

**Takeaway:** MCP tools that do heavy lifting locally are more reliable than exposing low-level building blocks for the LLM to orchestrate.

---

# Generated REST Clients Are Fragile

The typed clients (from `openapi-python-client` / `@hey-api/openapi-ts`) break when Teamscale's API changes a field name or type — even if the endpoint still works.

**Alternatives:**
- Build MCP tools into `teamscale-dev` (stays in sync automatically)
- Skip the generated client, use plain HTTP calls

---

<!-- _class: lead -->

# 🔮 Future Work

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

# Safer Authentication

| Method | ⚠️ Risk |
|---|---|
| **Env vars** | Must be set on start, MCP fails |
| **In-prompt** | **Credentials sent to the LLM** as tool parameters |

**Possible improvements:**
- 🔑 **OAuth / SSO** — browser-based login, token stored locally, never sent to LLM
- 🗝️ **System keychain** — read from OS keychain
- 📄 **Local config file** — `.teamscale.json` not exposed as params

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
| **Local install** | Separate plugin | Already on the machine | No | No |
| **Up-to-date** | User updates | With teamscale-dev | OPS updates | With Teamscale updates |
| **API version sync** | Manual (spec bundled) | Automatic | Manual | Automatic |
| **Auth solved** | ❌ | ✅ | ❌ | ✅ |

---

<!-- _class: lead -->

# Why teamscale-dev Is the Right Choice

---

# teamscale-dev Solves the Hard Problems

| Problem | Standalone Plugin | teamscale-dev |
|---|---|---|
| **API version drift** | Bundled spec goes stale | Handles different Teamscale versions and APIs |
| **Pre-commit payload** | LLM mangling, false findings | Reads files from disk, no limits |
| **Authentication** | Env vars or in-prompt (insecure) | Already manages credentials |
| **Installation** | Separate plugin install | Already on the machine |
| **Maintenance** | Separate repo, manual updates | Built by the Teamscale developers |

---

# How to Split the Work

| | Plugin | teamscale-dev |
|---|---|---|
| **Skills** | ✅ Slash commands | |
| **MCP tools** | | ✅ All tools live here |
| **Authentication** | | ✅ Credentials stay local |
| **Install** | Installs/references teamscale-dev | |

The plugin ships **skills only** and points to `teamscale-dev` as the MCP server (installing it if needed). No MCP tools in the plugin itself.

---

<!-- _class: lead -->

# 💬 Questions?
