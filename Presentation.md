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

Teamscale + Claude Code — findings, fixes, and test gaps from the command line.

1. **MCP Server** — exposes Teamscale REST API as tools Claude can call
2. **Skills** — multi-step workflows developers actually want to run

Three MCP server implementations. Five skills.

<!--
We connected Teamscale to Claude Code so developers can run findings analysis, fix code quality issues, and close test gaps — all from the command line.

The stack has two layers. The MCP server is the low-level bridge — it exposes Teamscale REST API endpoints as tools Claude can call. Skills sit on top and orchestrate those tools into things developers actually want to do, like "check my changes before pushing" or "fix findings on my MR."

We built three MCP server implementations to compare approaches, and five skills that demonstrate the real value.
-->

---

# 🔌 MCP in 30 Seconds

**Model Context Protocol** — connects AI assistants to external tools and data.

- **Tools** — actions Claude can invoke
- **Resources** — data Claude can read

Claude Code has native MCP support via its **plugin system**.

<!--
MCP is an open protocol that lets AI assistants call external tools and read external data. An MCP server exposes tools — actions the model can invoke, like "list projects" or "get findings" — and resources, which are read-only data endpoints.

Claude Code has native MCP support through its plugin system, so any MCP server can be installed as a plugin. We built three plugins that bridge Claude Code to the Teamscale REST API, each with a different approach to see what works best in practice.
-->

---

# 🗺️ Three MCP Server Approaches

| | Python OpenAPI | Python Custom | TypeScript Custom |
|---|---|---|---|
| **Strategy** | Auto-generate from spec | Hand-craft curated tools | Hand-craft curated tools |
| **API coverage** | Full (121 endpoints) | ~20 selected tools | 13 selected tools |
| **Server code** | 65 lines | ~700 lines | 535 lines |
| **Runtime** | Python + uv | Python + uv | Node.js 18+ |
| **Zero-config** | ❌ Env vars required | ✅ | ✅ |

<!--
We tried three different approaches to building the MCP server. The first auto-generates everything from the OpenAPI spec — minimal code, full coverage, but no curation. The other two are hand-crafted: we picked the endpoints developers actually need and added business logic on top.

The Python and TypeScript custom servers expose identical tools — same functionality, different runtimes. This let us compare the developer experience of building MCP servers in both languages. The custom servers also support zero-config installation: connection params can be passed per tool call, falling back to environment variables.
-->

---

# OpenAPI based — Full Auto

Auto-registers all 121 endpoints from the OpenAPI spec.

<div class="columns">
<div>

### ✅ Advantages

- Near-zero maintenance
- New endpoints automatically
- 65 lines of code

</div>
<div>

### ⚠️ Problems

- 121 tools flood Claude's context
- Claude picks wrong endpoint
- No business logic
- Env vars required at startup

</div>
</div>

<!--
This approach fetches the OpenAPI spec from a running Teamscale instance at startup and auto-registers every endpoint. It's incredibly low-effort — only 65 lines of server code — and you never have to update it when new API endpoints are added.

But in practice, it doesn't work well. 121 tools overwhelm Claude's context window. Claude frequently picks the wrong endpoint because many have similar names and descriptions. There's no higher-level business logic — it's just raw API calls. And you have to set environment variables before starting, which makes installation harder.
-->

---

# Custom Plugins — Curated Tools

<div class="columns">
<div>

### ✅ Advantages

- Claude picks the right tool reliably
- Higher-level business logic
- Zero-config install

</div>
<div>

### ⚠️ Limitations

- New endpoints requires manual work

</div>
</div>

Python and TypeScript versions expose identical tools.

<!--
The custom plugins are hand-written. We picked the ~20 endpoints developers actually need and added business logic on top — things like aggregating findings by file, verifying architecture, or detecting the right project from the git remote URL.

The tools have uniform error handling and optional connection parameters. You can pass server, user, and access key per tool call, or let it fall back to environment variables. This means zero-config installation — the plugin just works.

Claude reliably picks the right tool because the set is small and each tool has a clear, distinct purpose. The tradeoff is that every new endpoint requires manual work to add.

We built both a Python and TypeScript version with identical tools to compare the developer experience.
-->

---

# Quick Comparison

| Dimension | Python OpenAPI | Python Custom | TS Custom |
|---|---|---|---|
| **Endpoints** | 121 | ~20 | 13 |
| **Zero-config install** | ❌ | ✅ | ✅ |
| **Auto new endpoints** | ✅ | ❌ | ❌ |
| **Business logic** | ❌ | ✅ | ✅ |
| **Claude picks correctly** | Unreliable | Reliable | Reliable |

**Verdict:** Curated beats auto-generated. Small tool sets win.

<!--
The auto-generated approach sounds appealing — zero maintenance, full coverage — but it fails in practice. When Claude has 121 tools to choose from, it frequently picks the wrong one. There's no business logic to guide it, and the raw API responses aren't formatted for developer consumption.

Claude works much better with a small, curated tool set where each tool has a clear purpose. The custom plugins require more upfront work but deliver reliable results.
-->

---

<!-- _class: lead -->

# 🛠️ How To Use MCP Tools

## Skills Turn Tools Into Workflows

---

# Skills Are the Point

MCP tools are building blocks. **Skills** turn them into workflows.

```
/teamscale-skills:pre-commit                # "check my changes"
/teamscale-skills:merge-request-findings    # "what did my MR break?"
/teamscale-skills:fix-findings              # "fix them"
```

<!--
MCP tools alone are just building blocks. Without skills, the user must know which tools exist, in what order to call them, and how to interpret raw API results. That's a lot to ask.

Skills are slash commands that orchestrate tools, read code, edit files, and guide the user through multi-step workflows. With skills, the user just says what they want to accomplish. The skill handles project detection, tool orchestration, result formatting, and follow-up suggestions.

This is where the real value lives — not in the API bridge, but in the workflows built on top of it.
-->

---

# How Skills Work

A Markdown file. No code — just step-by-step instructions for Claude.

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

<!--
A skill is a Markdown file with YAML frontmatter — name and description. The body contains step-by-step instructions that tell Claude what to do. No code, no logic, just natural language instructions.

Skills can orchestrate MCP tools, Bash commands, and file operations into coherent workflows. They can read code, edit files, call multiple API endpoints in sequence, and present results in a developer-friendly format.

The key insight is that you don't need code to build powerful workflows. Claude follows the instructions, and the skill file is easy to read, edit, and extend.
-->

---

# The Five Skills

| Skill | What It Does |
|-------|-------------|
| **pre-commit** | Run Teamscale pre-commit analysis on uncommitted changes. Shows findings by file. |
| **merge-request-findings** | Auto-detect the MR for the current branch, fetch finding churn (added + in changed code). |
| **fix-findings** | Walk through findings one by one, propose code fixes, apply with confirmation. |
| **merge-request-test-gaps** | Show which changed methods in your MR lack test coverage. |
| **close-test-gaps** | For new methods: propose and write tests. For modified methods: suggest which tests to re-run. |


<!--
Let me walk through each skill:

Pre-commit runs Teamscale's pre-commit analysis on your uncommitted changes and shows findings grouped by file.

Merge-request-findings auto-detects the MR for your current branch and fetches the finding churn — both newly added findings and findings in changed code.

Fix-findings walks through findings one by one, proposes code fixes, and applies them with your confirmation.

Merge-request-test-gaps shows which changed methods in your MR lack test coverage.

Close-test-gaps has two modes: for new methods, it proposes and writes tests. For modified methods, it suggests which existing tests to re-run.
-->

---

# A Typical Developer Workflow

```
/teamscale-skills:pre-commit              # 1. Check my changes
/teamscale-skills:fix-findings            # 2. Fix the findings
/teamscale-skills:merge-request-findings  # 3. See MR findings
/teamscale-skills:fix-findings            # 4. Fix them too
/teamscale-skills:merge-request-test-gaps # 5. Check test gaps
/teamscale-skills:close-test-gaps         # 6. Write tests / re-run
```

Auto-detects project and MR. Skills chain naturally.

<!--
Each skill auto-detects the Teamscale project by matching the git remote URL against connector URLs, and detects the merge request by matching the current branch. You never have to type a project name or MR number.

Later skills also pick up context from earlier ones in the same conversation. If you ran pre-commit and then fix-findings, the fix skill already knows which findings were found — no need to re-fetch.

This is the workflow we envision: a developer pushes their feature branch, opens a conversation, runs through these skills, and their code is analyzed, fixed, and tested — all from the command line.
-->

---

# Why Skills Matter

**Without skills** — user drives every step:
```
"Check architecture violations in project X"
  → Claude calls one tool → raw results
```

**With skills** — user states the goal:
```
/teamscale-skills:pre-commit
  → detects project → reads changes → runs analysis
  → formats results → suggests fixes
```

<!--
This is the key difference. With only MCP tools, the user must know which tools exist, pass the right parameters, and interpret raw API responses. They're essentially driving Claude step by step.

With skills, the user just invokes a slash command. The skill handles everything: detecting the project from the git remote, reading the relevant changes, calling the right API endpoints in the right order, formatting the results, and suggesting next steps. It's the difference between giving someone a toolbox and giving them a contractor.
-->

---

# The Plugin Is Live

```
/plugins marketplace add https://github.com/...teamscale-claude-marketplace.git
/plugins install teamscale-mcp
/plugins install teamscale-skills
/reload-plugins
```

Skills work with any MCP server backend.

<!--
The marketplace ships multiple MCP server plugins. The user picks the one that fits their setup — teamscale-dev if they already have the CLI installed, or one of the custom servers otherwise. Then they install the skills plugin on top.

The skills are backend-agnostic: they work with any of the MCP servers. You can swap the backend without changing any workflows. This decoupling was intentional — it means we can improve or replace the MCP server layer without touching the skills.
-->

---

<!-- _class: lead -->

# 🔍 Observations

---

# LLM-Driven Pre-Commit Has Limits

File contents sent through the LLM hit payload limits
  &rarr; Claude silently strips content &rarr; **false findings**

`teamscale-dev` reads files from disk directly — no size limits, no mangling.

**Takeaway:** Local tools beat LLM-orchestrated building blocks.

<!--
The pre-commit skill sends file contents through the LLM as MCP tool parameters. When files are large, this hits payload size limits. Claude silently strips comments and constants to make things fit, which produces false findings — Teamscale sees code that's different from what's actually on disk.

teamscale-dev handles this natively. It reads files directly from disk with no size limits or content mangling. The LLM makes one tool call — "run pre-commit" — and gets clean results back.

The takeaway is that MCP tools that do heavy lifting locally are more reliable than exposing low-level building blocks for the LLM to orchestrate. Don't make the LLM read files and pass them to APIs when you can have the tool read files directly.
-->

---

# Generated REST Clients Are Fragile

Typed clients break when Teamscale's API changes a field name or type.

**Alternatives:**
- Build MCP into `teamscale-dev` (stays in sync)
- Host `/mcp` in Teamscale itself (always in sync)
- Skip generated clients, use plain HTTP

<!--
The typed clients from openapi-python-client and hey-api/openapi-ts are generated from a bundled OpenAPI spec. When Teamscale's API changes a field name or type — even if the endpoint still works — the generated client breaks with deserialization errors.

This is a maintenance burden. Every Teamscale release could potentially break the plugin. The alternatives all solve this by keeping the tools closer to the API: building them into teamscale-dev means they ship with the same release cycle, hosting an /mcp endpoint in Teamscale itself means the server and API are always in sync, and plain HTTP calls avoid typed deserialization entirely.
-->

---

<!-- _class: lead -->

# 🔮 Future Work

---

# Skill-Driven Development

```
User use case  →  Design skill  →  Implement MCP tools skill needs
```

- "Check my changes" &rarr; pre-commit skill &rarr; `pre_commit_analyze`
- "MR findings?" &rarr; merge-request-findings &rarr; `get_merge_request_finding_churn`
- "Close test gaps" &rarr; close-test-gaps &rarr; `get_test_gap_treemap`

**The MCP tools exist to serve the skills.**

<!--
This is the key design principle: skills dictate which MCP tools to build — not the other way around. You start from a developer use case, design the skill workflow, and then implement only the MCP tools that skill needs.

We started from three developer workflows. "Check my changes before pushing" drove the pre-commit skill, which needed the pre_commit_analyze tool. "What findings does my MR have?" drove the merge-request-findings skill, which needed list_merge_requests and get_merge_request_finding_churn. "Close my test gaps" drove the close-test-gaps skill, which needed get_test_gap_treemap and get_merge_request_test_suggestions.

If you build tools first and hope someone uses them, you get 121 endpoints nobody orchestrates. If you start from skills, you get exactly the tools developers need.
-->

---

# Safer Authentication

| Current | Risk |
|---|---|
| **Env vars** | Must be set, MCP fails if missing |
| **In-prompt** | **Credentials sent to the LLM** |

**Improvements:**
- 🔑 **OAuth / SSO** — browser login, token stays local
- 🗝️ **System keychain** — OS-level credential storage
- 📄 **Config file** — `.teamscale.json`, never exposed as params

<!--
Right now there are two authentication options, and both have problems. Environment variables must be set before the MCP server starts — if they're missing, the server fails. The alternative is passing credentials in-prompt as tool parameters, which means they're sent to the LLM. Neither is ideal.

We see three possible improvements. OAuth or SSO would use browser-based login with a token stored locally that never reaches the LLM. System keychain integration would read credentials from the OS keychain. A local config file like .teamscale.json could store connection details without exposing them as tool parameters.
-->

---

# More Plugin Layers

| Component | Teamscale Example |
|---|---|
| ✅ **MCP Server** | `get_findings_list`, `verify_architecture` |
| ✅ **Skills** | `/pre-commit`, `/fix-findings` |
| **Agents** | "Teamscale QA" persona |
| **Hooks** | Architecture check on every commit |
| **Monitors** | Watch worker logs for fatals |

**Next:** User use cases &rarr; skills &rarr; tools.

<!--
We built MCP tools and skills, but a Claude Code plugin can ship more. Agents are custom personas with their own system prompt — imagine a "Teamscale QA" agent that automatically reviews code quality. Hooks auto-run on Claude Code events — like checking architecture on every commit. Monitors are background watchers that could, for example, watch Teamscale worker logs for fatals and alert you.

The path forward is the same skill-driven approach: collect user use cases, design skills around them, then implement the tools those skills need.
-->

---

<!-- _class: lead -->

# 🏗️ Architecture

## Where Should Everything Live?

---

# Plugin Distribution

The **plugin** (skills, config, metadata) needs a home:

- **Our GitHub repo** — works today, we control releases
- **Public Claude Code Marketplace** — broader reach, discoverability

Either way, the plugin ships skills + a pointer to the MCP server.

The open question is **where the MCP server runs**.

<!--
The plugin itself — skills, configuration, metadata — is straightforward to distribute. We can host it in our own GitHub repository, which works today and gives us full control over releases. Or we publish it to the public Claude Code marketplace for broader reach and discoverability.

Either option works, and the plugin content is the same: skills plus a reference to the MCP server backend. The skills are just Markdown files, so distribution is simple.

The real architectural question is where the MCP server lives — that's where the tradeoffs get interesting. So let's focus on that.
-->

---

# MCP Hosting Options

| | Standalone Plugin | teamscale-dev | Teamscale /mcp |
|---|---|---|---|
| **Local install** | Separate plugin | Already on machine | Thin local MCP |
| **Up-to-date** | User updates | With teamscale-dev release | With Teamscale release |
| **API sync** | Manual | Automatic | Automatic |
| **Auth** | ❌ | ✅ | ✅ |

We prototyped the standalone plugin. Two better options emerged:

<!--
The standalone plugin is what we built for this project. It works, but it has maintenance overhead — the user has to update it separately, the OpenAPI spec is bundled and can drift, and authentication isn't solved.

Two better options emerged during the project. teamscale-dev already handles credentials and API versioning, so building MCP tools into it gives you all that for free. Alternatively, hosting an /mcp endpoint directly in Teamscale means the API and tools are always in sync, and auth is server-side.
-->

---

# Option A: teamscale-dev as MCP Server

| Component | Plugin | teamscale-dev |
|---|---|---|
| **Skills** | ✅ | |
| **MCP tools / resources** | | ✅ |
| **Auth** | | ✅ Local credentials |
| **File access** | | ✅ Reads disk directly |

Plugin ships **skills only** + links to `teamscale-dev` as MCP server.

<!--
teamscale-dev already manages credentials, handles API versioning, and reads files from disk. It already has an MCP mode — teamscale-dev mcp — that we've been using.

In this model, the plugin is minimal: it ships skills and a pointer to teamscale-dev as the MCP server backend. No generated client, no API drift, no auth issues. teamscale-dev still talks to a remote Teamscale server, but the plugin itself is simple — just skills and configuration.
-->

---

# Option B: Teamscale /mcp + Local MCP

| Component | Plugin | /mcp | Local MCP |
|---|---|---|---|
| **Skills** | ✅ | | |
| **MCP tools / resources** | | ✅ | |
| **Auth** | ✅ OAuth/OpenID | *Only receives token* |  |
| **File access** | | | ✅ Reads disk directly |

<!--
This option splits the work between a remote MCP hosted by Teamscale and a thin local MCP for filesystem operations.

The remote MCP handles everything that lives on the server — findings, metrics, test gaps, merge requests. Auth is server-side: the local MCP handles login and only passes a token to /mcp. The local MCP also handles everything that needs the filesystem: constructing diffs, reading file contents, building change lists for pre-commit.
-->

---

# Option B: Why Split?

- **Remote MCP** — all Teamscale data, auto-versioning
- **Local MCP** — filesystem ops: diffs, file reads, change lists

**Strength:** Thin local footprint, zero API drift, works with any MCP client.

<!--
The remote MCP serves all Teamscale data — findings, test gaps, merge requests, dashboards. Auth is server-side, API versioning is automatic, and every Teamscale update ships new tools immediately. No plugin update needed.

The local MCP handles everything that needs the filesystem — constructing diffs, reading file contents, building change lists for pre-commit. It's thin and rarely changes.

The key strength is that these tools are available to any MCP client, not just Claude Code. Any AI assistant that speaks MCP could connect to Teamscale's /mcp endpoint. That's a much broader reach than a Claude Code-specific plugin.
-->

---

# Comparing the Two

| Dimension | teamscale-dev | /mcp + Local MCP |
|---|---|---|
| **Install** | Single binary / Link from plugin | Thin local MCP from plugin |
| **API drift** | CLI handles it | Server handles it |
| **Auth** | CLI credentials | OAuth/OpenID |
| **Server changes** | None | New endpoint |
| **Ships with** | teamscale-dev | Teamscale release |
| **Beyond Claude Code** | No | Yes (any MCP client) |

Both need a **skills plugin** for developer workflows.

<!--
Both options solve the core problems — API drift and authentication — but they make different tradeoffs.

teamscale-dev is simpler: single binary, no server changes, works offline. But it's CLI-specific — only Claude Code can use it.

The /mcp endpoint requires server changes but has broader reach. Any MCP client can connect to it, not just Claude Code. New tools ship with every Teamscale release automatically.

Both still need a skills plugin to turn the raw tools into developer workflows. The skills are the constant — the MCP backend is the variable.
-->

---

<!-- _class: lead -->

# 💬 Questions?
