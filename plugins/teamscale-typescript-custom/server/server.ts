import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import {
  createClient,
  createConfig,
  type Client,
} from "./teamscale-rest-api-client/client/index.js";
import {
  getAllProjects,
  getProjectConfiguration,
  getBranchesGetRequest,
  deleteProject,
  getProjectWorkerLogs,
  getFindings,
  getAllDashboards,
  getAllArchitectureAssessments,
  getArchitectureAssessment,
} from "./teamscale-rest-api-client/sdk.gen.js";
import type {
  ProjectInfo,
  ConnectorConfiguration,
} from "./teamscale-rest-api-client/types.gen.js";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeClient(server: string, user: string, accessKey: string): Client {
  return createClient(
    createConfig({
      baseUrl: server,
      auth: `${user}:${accessKey}`,
    })
  );
}

function resolveConnection(
  server?: string,
  user?: string,
  accessKey?: string
): Client {
  server = server ?? process.env.TEAMSCALE_URL;
  user = user ?? process.env.TEAMSCALE_USER;
  accessKey = accessKey ?? process.env.TEAMSCALE_ACCESS_KEY;

  if (!server || !user || !accessKey) {
    throw new Error(
      "Teamscale server, user, and access_key must be provided as arguments or set via TEAMSCALE_URL, TEAMSCALE_USER, and TEAMSCALE_ACCESS_KEY environment variables"
    );
  }
  return makeClient(server, user, accessKey);
}

async function teamscaleFetch<T>(
  result: {
    data: T | undefined;
    error: unknown;
    response: Response;
    request: Request;
  },
  expectBody = true
): Promise<T> {
  const { data, error, response } = result;
  if (response.status === 401) {
    throw new Error("Authentication failed: check user and access_key");
  }
  if (response.status === 403) {
    throw new Error("Access denied: the user does not have permission");
  }
  if (!response.ok) {
    throw new Error(
      `Teamscale returned unexpected status ${response.status}`
    );
  }
  if (expectBody && data === undefined) {
    throw new Error(
      "Teamscale returned 200 but the response could not be parsed"
    );
  }
  return data as T;
}

// Common connection params reused in every tool schema
const connectionParams = {
  server: z.string().optional().describe("Teamscale server URL"),
  user: z.string().optional().describe("Teamscale user name"),
  access_key: z.string().optional().describe("Teamscale access key"),
};

function textResult(value: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(value, null, 2) }] };
}

// ---------------------------------------------------------------------------
// MCP Server
// ---------------------------------------------------------------------------

const server = new McpServer({ name: "Teamscale MCP", version: "0.1.0" });

// ---- list_projects ----

server.tool(
  "list_projects",
  "List all projects on a Teamscale instance.",
  { ...connectionParams },
  async ({ server: srv, user, access_key }) => {
    const client = resolveConnection(srv, user, access_key);
    const projects = await teamscaleFetch(
      await getAllProjects({ client })
    );
    return textResult(projects);
  }
);

// ---- get_project_id ----

server.tool(
  "get_project_id",
  "Find the Teamscale project ID(s) for a given repository URL.",
  {
    url: z.string().describe("Repository URL to search for"),
    ...connectionParams,
  },
  async ({ url, server: srv, user, access_key }) => {
    const client = resolveConnection(srv, user, access_key);

    const normalize = (u: string) =>
      u.replace(/\/+$/, "").replace(/\.git$/, "").toLowerCase();

    const connectorUrl = (
      connector: ConnectorConfiguration
    ): string | undefined => {
      const opts = connector.options;
      if (!opts) return undefined;
      const t = connector.type.toLowerCase();

      if (t === "github") {
        const serverUrl = opts["GitHub Server URL"] ?? "";
        const repoPath = opts["Repository Path"] ?? "";
        if (serverUrl && repoPath) {
          return serverUrl.replace(/\/+$/, "") + "/" + repoPath;
        }
      }
      if (t === "stash" || t === "bitbucket") {
        const serverUrl = opts["Stash Server URL"] ?? "";
        const repoPath = opts["Repository Path"] ?? "";
        if (serverUrl && repoPath) {
          return serverUrl.replace(/\/+$/, "") + "/" + repoPath;
        }
      }
      const key = connector.connectorIdentifierOptionName;
      return key && opts[key] ? opts[key] : undefined;
    };

    const projects = await teamscaleFetch(
      await getAllProjects({ client })
    );

    const configs = await Promise.all(
      projects
        .filter((p: ProjectInfo) => p.publicIds?.length)
        .map(async (p: ProjectInfo) => {
          const config = await teamscaleFetch(
            await getProjectConfiguration({
              client,
              path: { project: p.publicIds[0] },
            })
          );
          return { projectId: p.publicIds[0], config };
        })
    );

    const normalizedUrl = normalize(url);
    for (const { projectId, config } of configs) {
      if (!config) continue;
      for (const connector of config.connectors ?? []) {
        const candidate = connectorUrl(connector);
        if (candidate && normalize(candidate) === normalizedUrl) {
          const match = projects.find(
            (p: ProjectInfo) => p.publicIds?.[0] === projectId
          );
          return textResult(match!.publicIds);
        }
      }
    }

    throw new Error(`No Teamscale project found with repository URL: ${url}`);
  }
);

// ---- get_project_connectors ----

server.tool(
  "get_project_connectors",
  "Return the raw connector options for a Teamscale project (for debugging).",
  {
    project: z.string().describe("The Teamscale project ID"),
    ...connectionParams,
  },
  async ({ project, server: srv, user, access_key }) => {
    const client = resolveConnection(srv, user, access_key);
    const config = await teamscaleFetch(
      await getProjectConfiguration({ client, path: { project } })
    );
    return textResult(config.connectors);
  }
);

// ---- get_project_branches ----

server.tool(
  "get_project_branches",
  "Get all live branches for a Teamscale project.",
  {
    project: z.string().describe("The Teamscale project ID"),
    ...connectionParams,
  },
  async ({ project, server: srv, user, access_key }) => {
    const client = resolveConnection(srv, user, access_key);
    const branches = await teamscaleFetch(
      await getBranchesGetRequest({ client, path: { project } })
    );
    return textResult(branches.liveBranches);
  }
);

// ---- get_worker_logs ----

server.tool(
  "get_worker_logs",
  "Get all worker log entries for a Teamscale project.",
  {
    project: z.string().describe("The Teamscale project ID"),
    ...connectionParams,
  },
  async ({ project, server: srv, user, access_key }) => {
    const client = resolveConnection(srv, user, access_key);
    const logs = await teamscaleFetch(
      await getProjectWorkerLogs({ client, path: { project } })
    );
    return textResult(logs.logEntries);
  }
);

// ---- get_worker_log_warnings ----

server.tool(
  "get_worker_log_warnings",
  "Get warning-level worker log entries for a Teamscale project (excludes fatals).",
  {
    project: z.string().describe("The Teamscale project ID"),
    ...connectionParams,
  },
  async ({ project, server: srv, user, access_key }) => {
    const client = resolveConnection(srv, user, access_key);

    const [warnResp, fatalResp] = await Promise.all([
      teamscaleFetch(
        await getProjectWorkerLogs({
          client,
          path: { project },
          query: { minLogLevel: "WARN" },
        })
      ),
      teamscaleFetch(
        await getProjectWorkerLogs({
          client,
          path: { project },
          query: { minLogLevel: "FATAL" },
        })
      ),
    ]);

    const fatalIds = new Set(fatalResp.logEntries.map((e) => e.id));
    const warnings = warnResp.logEntries.filter((e) => !fatalIds.has(e.id));
    return textResult(warnings);
  }
);

// ---- get_worker_log_fatals ----

server.tool(
  "get_worker_log_fatals",
  "Get fatal worker log entries for a Teamscale project.",
  {
    project: z.string().describe("The Teamscale project ID"),
    ...connectionParams,
  },
  async ({ project, server: srv, user, access_key }) => {
    const client = resolveConnection(srv, user, access_key);
    const logs = await teamscaleFetch(
      await getProjectWorkerLogs({
        client,
        path: { project },
        query: { minLogLevel: "FATAL" },
      })
    );
    return textResult(logs.logEntries);
  }
);

// ---- get_findings_count_per_file ----

server.tool(
  "get_findings_count_per_file",
  "Return the number of findings per file for a Teamscale project. Useful for spotting files with an unusually high finding count, which may indicate third-party code that should be excluded from analysis.",
  {
    project: z.string().describe("The Teamscale project ID"),
    uniform_path: z.string().optional().default(""),
    t: z.string().optional().describe("Commit/timestamp descriptor"),
    baseline: z.string().optional().describe("Baseline name or timestamp"),
    ...connectionParams,
  },
  async ({ project, uniform_path, t, baseline, server: srv, user, access_key }) => {
    const client = resolveConnection(srv, user, access_key);
    const findings = await teamscaleFetch(
      await getFindings({
        client,
        path: { project },
        query: {
          "uniform-path": uniform_path || undefined,
          t: t ?? undefined,
          baseline: baseline ?? undefined,
          all: true,
        },
      })
    );

    const result: Record<string, number> = {};
    for (const f of findings) {
      const location = f.location as { uniformPath?: string };
      const path = location?.uniformPath || "<unknown>";
      result[path] = (result[path] || 0) + 1;
    }
    const sorted = Object.fromEntries(
      Object.entries(result).sort(([, a], [, b]) => b - a)
    );
    return textResult(sorted);
  }
);

// ---- get_findings_count_per_check ----

server.tool(
  "get_findings_count_per_check",
  "Return the number of findings per check (type) for a Teamscale project, sorted descending. Useful for identifying individual checks that produce an outrageous number of findings and may need to be disabled.",
  {
    project: z.string().describe("The Teamscale project ID"),
    uniform_path: z.string().optional().default(""),
    t: z.string().optional().describe("Commit/timestamp descriptor"),
    baseline: z.string().optional().describe("Baseline name or timestamp"),
    ...connectionParams,
  },
  async ({ project, uniform_path, t, baseline, server: srv, user, access_key }) => {
    const client = resolveConnection(srv, user, access_key);
    const findings = await teamscaleFetch(
      await getFindings({
        client,
        path: { project },
        query: {
          "uniform-path": uniform_path || undefined,
          t: t ?? undefined,
          baseline: baseline ?? undefined,
          all: true,
        },
      })
    );

    const counts: Record<string, number> = {};
    for (const f of findings) {
      counts[f.typeName] = (counts[f.typeName] || 0) + 1;
    }
    const sorted = Object.fromEntries(
      Object.entries(counts).sort(([, a], [, b]) => b - a)
    );
    return textResult(sorted);
  }
);

// ---- verify_project_dashboards ----

server.tool(
  "verify_project_dashboards",
  "Verify the existence of the overview, system, and test code dashboards for a project. Returns which of the three expected dashboards exist and which are missing, plus the full list of dashboards found for the project.",
  {
    project: z.string().describe("The Teamscale project ID"),
    ...connectionParams,
  },
  async ({ project, server: srv, user, access_key }) => {
    const client = resolveConnection(srv, user, access_key);
    const dashboards = await teamscaleFetch(
      await getAllDashboards({ client, query: { project } })
    );

    const found = dashboards.map((d) => ({ id: String(d.id), name: d.name }));
    const namesLower = found.map((d) => d.name.toLowerCase());

    const expected = ["overview", "system code", "test code"];
    return textResult({
      found,
      expected: Object.fromEntries(
        expected.map((label) => [
          label,
          namesLower.some((name) => name.includes(label)),
        ])
      ),
    });
  }
);

// ---- verify_architecture ----

server.tool(
  "verify_architecture",
  "Verify the architecture of a Teamscale project. For each architecture, returns the violation count and any dependency edges pointing from a System component to a Tests component, which indicates that test code may not be correctly separated in the architecture.",
  {
    project: z.string().describe("The Teamscale project ID"),
    t: z.string().optional().describe("Commit/timestamp descriptor"),
    ...connectionParams,
  },
  async ({ project, t, server: srv, user, access_key }) => {
    const client = resolveConnection(srv, user, access_key);

    const overviews = await teamscaleFetch(
      await getAllArchitectureAssessments({
        client,
        path: { project },
        query: { t: t ?? undefined },
      })
    );

    const assessments = await Promise.all(
      overviews.map(async (o) => {
        const assessment = await teamscaleFetch(
          await getArchitectureAssessment({
            client,
            path: { project, uniformPath: o.uniformPath },
            query: { t: t ?? undefined },
          })
        );
        return { overview: o, assessment };
      })
    );

    const results = assessments.map(({ overview, assessment }) => {
      const systemToTests: Array<{ from: string; to: string }> = [];
      for (const policy of assessment.policies ?? []) {
        if (policy.from.toLowerCase().includes("system")) {
          for (const dep of policy.dependencies ?? []) {
            if (dep.to.toLowerCase().includes("test")) {
              systemToTests.push({ from: policy.from, to: dep.to });
            }
          }
        }
      }
      return {
        architecture: overview.uniformPath,
        violations: overview.violations,
        system_to_tests_dependencies: systemToTests,
      };
    });

    return textResult(results);
  }
);

// ---- delete_teamscale_project ----

server.tool(
  "delete_teamscale_project",
  "Delete a Teamscale project, including its dashboards and assignments.",
  {
    project: z.string().describe("The Teamscale project ID"),
    ...connectionParams,
  },
  async ({ project, server: srv, user, access_key }) => {
    const client = resolveConnection(srv, user, access_key);
    await teamscaleFetch(
      await deleteProject({
        client,
        path: { project },
        query: {
          "force-delete": true,
          "delete-all-assignments": true,
          "delete-all-dashboards": true,
        },
      }),
      false
    );
    return textResult(`Project '${project}' deleted.`);
  }
);

// ---- get_findings_list ----

server.tool(
  "get_findings_list",
  "Fetch all findings for a Teamscale project via /api/projects/{project}/findings/list.",
  {
    project: z.string().describe("The Teamscale project ID"),
    uniform_path: z.string().optional().default(""),
    t: z.string().optional().describe("Commit/timestamp descriptor"),
    baseline: z.string().optional().describe("Baseline name or timestamp"),
    ...connectionParams,
  },
  async ({ project, uniform_path, t, baseline, server: srv, user, access_key }) => {
    const client = resolveConnection(srv, user, access_key);
    const findings = await teamscaleFetch(
      await getFindings({
        client,
        path: { project },
        query: {
          "uniform-path": uniform_path || undefined,
          t: t ?? undefined,
          baseline: baseline ?? undefined,
          all: true,
        },
      })
    );
    return textResult(findings);
  }
);

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main();
