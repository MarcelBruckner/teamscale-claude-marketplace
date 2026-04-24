import base64
import functools
import inspect
import asyncio
import json
import os
import httpx

from typing import Any
from collections.abc import Awaitable, Callable, Coroutine
from mcp.server.fastmcp import FastMCP

from teamscale_rest_api_client import AuthenticatedClient
from teamscale_rest_api_client.api.project import delete_project, get_all_projects, get_branches_get_request, get_project_configuration
from teamscale_rest_api_client.api.logging import get_project_worker_logs
from teamscale_rest_api_client.api.findings import get_finding as api_get_finding, get_findings
from teamscale_rest_api_client.api.dashboards import get_all_dashboards
from teamscale_rest_api_client.api.architecture import get_all_architecture_assessments, get_architecture_assessment
from teamscale_rest_api_client.api.pre_commit import request_pre_commit_analysis, poll_pre_commit_results
from teamscale_rest_api_client.api.merge_requests import get_merge_request_finding_churn as api_get_merge_request_finding_churn
from teamscale_rest_api_client.models.e_log_level import ELogLevel
from teamscale_rest_api_client.models.request_pre_commit_analysis_body import RequestPreCommitAnalysisBody
from teamscale_rest_api_client.models.pre_commit_3_result import PreCommit3Result
from teamscale_rest_api_client.types import UNSET


MCP = FastMCP("Teamscale MCP")


def make_client(server: str, user: str, access_key: str) -> AuthenticatedClient:
    token = base64.b64encode(f"{user}:{access_key}".encode()).decode()
    return AuthenticatedClient(
        base_url=server,
        token=token,
        prefix="Basic",
        verify_ssl=False,
    )


def resolve_connection(server: str | None, user: str | None, access_key: str | None) -> AuthenticatedClient:
    server = server if server is not None else os.environ.get("TEAMSCALE_URL")
    user = user if user is not None else os.environ.get("TEAMSCALE_USER")
    access_key = access_key if access_key is not None else os.environ.get("TEAMSCALE_ACCESS_KEY")

    if not all([server, user, access_key]):
        raise ValueError("Teamscale server, user, and access_key must be provided as arguments or set via TEAMSCALE_URL, TEAMSCALE_USER, and TEAMSCALE_ACCESS_KEY environment variables")
    return make_client(server, user, access_key)


def teamscale_tool(func: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    """Decorator that injects a `fetch` helper into the tool, handling network errors
    and HTTP status checking generically for any Teamscale API call."""
    sig = inspect.signature(func)

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        async def fetch(coro: Awaitable, *, expect_body: bool = True) -> Any:
            try:
                response = await coro
            except httpx.ConnectError as e:
                raise RuntimeError(f"Could not connect to Teamscale: {e}") from e
            except httpx.TimeoutException as e:
                raise RuntimeError(f"Request to Teamscale timed out: {e}") from e
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"Teamscale returned an empty or invalid response body: {e}"
                ) from e
            if response.status_code == 401:
                raise PermissionError("Authentication failed: check user and access_key")
            if response.status_code == 403:
                raise PermissionError("Access denied: the user does not have permission")
            if not (200 <= response.status_code < 300):
                raise RuntimeError(f"Teamscale returned unexpected status {response.status_code}")
            if expect_body and response.parsed is None:
                raise RuntimeError("Teamscale returned a success status but the response could not be parsed")
            return response

        return await func(*args, **kwargs, fetch=fetch)

    # Remove 'fetch' from the public signature so FastMCP does not expose it as a tool parameter
    params = [p for name, p in sig.parameters.items() if name != "fetch"]
    wrapper.__signature__ = sig.replace(parameters=params)

    return wrapper





@MCP.tool()
@teamscale_tool
async def list_projects(
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> list[dict]:
    """List all projects on a Teamscale instance."""
    client = resolve_connection(server, user, access_key)
    response = await fetch(get_all_projects.asyncio_detailed(client=client))
    return [p.to_dict() for p in response.parsed]




@MCP.tool()
@teamscale_tool
async def get_project_id(
    url: str,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> list[str]:
    """Find the Teamscale project ID(s) for a given repository URL."""

    def normalize(u: str) -> str:
        return u.rstrip("/").removesuffix(".git").lower()

    def connector_url(connector) -> str | None:
        """Reconstruct the repo URL from connector options based on connector type."""
        opts = connector.options
        if connector.options is UNSET:
            return None
        t = connector.type_.lower()
        if t == "github":
            server_url = opts["GitHub Server URL"] if "GitHub Server URL" in opts else ""
            repo_path = opts["Repository Path"] if "Repository Path" in opts else ""
            if server_url and repo_path:
                return server_url.rstrip("/") + "/" + repo_path
        if t in ("stash", "bitbucket"):
            server_url = opts["Stash Server URL"] if "Stash Server URL" in opts else ""
            repo_path = opts["Repository Path"] if "Repository Path" in opts else ""
            if server_url and repo_path:
                return server_url.rstrip("/") + "/" + repo_path
        # Generic fallback: try the connector identifier key
        key = connector.connector_identifier_option_name
        return opts[key] if key in opts else None

    client = resolve_connection(server, user, access_key)

    projects_response = await fetch(get_all_projects.asyncio_detailed(client=client))
    projects = projects_response.parsed

    async def fetch_config(project_id: str):
        response = await fetch(get_project_configuration.asyncio_detailed(project=project_id, client=client))
        return project_id, response.parsed

    configs = await asyncio.gather(*[fetch_config(p.public_ids[0]) for p in projects if p.public_ids])

    normalized_url = normalize(url)
    for project_id, config in configs:
        if config is None:
            continue
        for connector in config.connectors or []:
            candidate = connector_url(connector)
            if candidate and normalize(candidate) == normalized_url:
                match = next(p for p in projects if p.public_ids and p.public_ids[0] == project_id)
                return match.public_ids

    raise RuntimeError(f"No Teamscale project found with repository URL: {url}")


@MCP.tool()
@teamscale_tool
async def get_project_connectors(
    project: str,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> list[dict]:
    """Return the raw connector options for a Teamscale project (for debugging)."""
    client = resolve_connection(server, user, access_key)
    response = await fetch(get_project_configuration.asyncio_detailed(project=project, client=client))
    return [c.to_dict() for c in response.parsed.connectors]


@MCP.tool()
@teamscale_tool
async def get_project_branches(
    project: str,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> list[str]:
    """Get all live branches for a Teamscale project."""
    client = resolve_connection(server, user, access_key)
    response = await fetch(get_branches_get_request.asyncio_detailed(project=project, client=client))
    return response.parsed.live_branches


@MCP.tool()
@teamscale_tool
async def get_worker_logs(
    project: str,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> list[dict]:
    """Get all worker log entries for a Teamscale project."""
    client = resolve_connection(server, user, access_key)
    response = await fetch(get_project_worker_logs.asyncio_detailed(project=project, client=client))
    return [e.to_dict() for e in response.parsed.log_entries]


@MCP.tool()
@teamscale_tool
async def get_worker_log_warnings(
    project: str,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> list[dict]:
    """Get warning-level worker log entries for a Teamscale project (excludes fatals)."""
    client = resolve_connection(server, user, access_key)

    warn_resp, fatal_resp = await asyncio.gather(
        fetch(get_project_worker_logs.asyncio_detailed(project=project, client=client, min_log_level=ELogLevel.WARN)),
        fetch(get_project_worker_logs.asyncio_detailed(project=project, client=client, min_log_level=ELogLevel.FATAL)),
    )

    warn_entries = warn_resp.parsed.log_entries
    fatal_ids = {e.id for e in fatal_resp.parsed.log_entries}
    return [e.to_dict() for e in warn_entries if e.id not in fatal_ids]


@MCP.tool()
@teamscale_tool
async def get_worker_log_fatals(
    project: str,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> list[dict]:
    """Get fatal worker log entries for a Teamscale project."""
    client = resolve_connection(server, user, access_key)
    response = await fetch(get_project_worker_logs.asyncio_detailed(project=project, client=client, min_log_level=ELogLevel.FATAL))
    return [e.to_dict() for e in response.parsed.log_entries]


@MCP.tool()
@teamscale_tool
async def get_findings_count_per_file(
    project: str,
    uniform_path: str = "",
    t: str | None = None,
    baseline: str | None = None,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> dict[str, int]:
    """Return the number of findings per file for a Teamscale project.

    Useful for spotting files with an unusually high finding count, which may
    indicate third-party code that should be excluded from analysis.
    """
    client = resolve_connection(server, user, access_key)
    response = await fetch(get_findings.asyncio_detailed(
        project=project,
        client=client,
        uniform_path=uniform_path,
        t=t if t is not None else UNSET,
        baseline=baseline if baseline is not None else UNSET,
        all_=True,
    ))

    result: dict[str, int] = {}
    for f in response.parsed:
        path = f.location.uniform_path or "<unknown>"
        result[path] = result.get(path, 0) + 1
    return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))


@MCP.tool()
@teamscale_tool
async def get_findings_count_per_check(
    project: str,
    uniform_path: str = "",
    t: str | None = None,
    baseline: str | None = None,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> dict[str, int]:
    """Return the number of findings per check (type) for a Teamscale project, sorted descending.

    Useful for identifying individual checks that produce an outrageous number of
    findings and may need to be disabled.
    """
    client = resolve_connection(server, user, access_key)
    response = await fetch(get_findings.asyncio_detailed(
        project=project,
        client=client,
        uniform_path=uniform_path,
        t=t if t is not None else UNSET,
        baseline=baseline if baseline is not None else UNSET,
        all_=True,
    ))

    counts: dict[str, int] = {}
    for f in response.parsed:
        counts[f.type_name] = counts.get(f.type_name, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


@MCP.tool()
@teamscale_tool
async def verify_project_dashboards(
    project: str,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> dict:
    """Verify the existence of the overview, system, and test code dashboards for a project.

    Returns which of the three expected dashboards exist and which are missing,
    plus the full list of dashboards found for the project.
    """
    client = resolve_connection(server, user, access_key)
    response = await fetch(get_all_dashboards.asyncio_detailed(client=client, project=project))

    dashboards = [{"id": str(d.id), "name": d.name} for d in response.parsed]
    names_lower = [d["name"].lower() for d in dashboards]

    expected = ["overview", "system code", "test code"]
    return {
        "found": dashboards,
        "expected": {
            label: any(label in name for name in names_lower)
            for label in expected
        },
    }


@MCP.tool()
@teamscale_tool
async def verify_architecture(
    project: str,
    t: str | None = None,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> list[dict]:
    """Verify the architecture of a Teamscale project.

    For each architecture, returns the violation count and any dependency edges
    pointing from a System component to a Tests component, which indicates that
    test code may not be correctly separated in the architecture.
    """
    client = resolve_connection(server, user, access_key)

    overview_response = await fetch(get_all_architecture_assessments.asyncio_detailed(
        project=project,
        client=client,
        t=t if t is not None else UNSET,
    ))
    overviews = overview_response.parsed

    async def assess(uniform_path: str):
        response = await fetch(get_architecture_assessment.asyncio_detailed(
            project=project,
            uniform_path=uniform_path,
            client=client,
            t=t if t is not None else UNSET,
        ))
        return uniform_path, response.parsed

    assessments = await asyncio.gather(*[assess(o.uniform_path) for o in overviews])

    results = []
    for o, (uniform_path, assessment) in zip(overviews, assessments):
        system_to_tests = []
        for policy in (assessment.policies or []):
            if "system" in policy.from_.lower():
                for dep in (policy.dependencies or []):
                    if "test" in dep.to.lower():
                        system_to_tests.append({"from": policy.from_, "to": dep.to})
        results.append({
            "architecture": uniform_path,
            "violations": o.violations,
            "system_to_tests_dependencies": system_to_tests,
        })
    return results

@MCP.tool()
@teamscale_tool
async def delete_teamscale_project(
    project: str,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> str:
    """Delete a Teamscale project, including its dashboards and assignments."""
    client = resolve_connection(server, user, access_key)
    await fetch(
        delete_project.asyncio_detailed(
            project=project,
            client=client,
            force_delete=True,
            delete_all_assignments=True,
            delete_all_dashboards=True,
        ),
        expect_body=False,
    )
    return f"Project '{project}' deleted."


@MCP.tool()
@teamscale_tool
async def get_findings_list(
    project: str,
    uniform_path: str = "",
    t: str | None = None,
    baseline: str | None = None,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> list[dict]:
    """Fetch all findings for a Teamscale project via /api/projects/{project}/findings/list."""
    client = resolve_connection(server, user, access_key)
    response = await fetch(get_findings.asyncio_detailed(
        project=project,
        client=client,
        uniform_path=uniform_path,
        t=t if t is not None else UNSET,
        baseline=baseline if baseline is not None else UNSET,
        all_=True,
    ))
    return [f.to_dict() for f in response.parsed]


@MCP.tool()
@teamscale_tool
async def get_finding(
    project: str,
    id: str,
    t: str | None = None,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> dict:
    """Fetch a single finding by its ID.

    Returns the full finding details including message, assessment, category,
    location, properties, and secondary locations.
    """
    client = resolve_connection(server, user, access_key)
    response = await fetch(api_get_finding.asyncio_detailed(
        project=project,
        id=id,
        client=client,
        t=t if t is not None else UNSET,
    ))
    return response.parsed.to_dict()


@MCP.tool()
@teamscale_tool
async def list_merge_requests(
    project: str,
    status: str | None = "OPEN",
    filter: str | None = None,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> list[dict]:
    """List merge requests for a Teamscale project.

    Returns merge requests with their source/target branches, title, status,
    and finding churn counts. Use status to filter (OPEN, MERGED, OTHER).
    Use filter for a case-insensitive regex match on the MR list.
    """
    client = resolve_connection(server, user, access_key)
    params: dict[str, Any] = {"max": -1}
    if status is not None:
        params["status"] = status
    if filter is not None:
        params["filter"] = filter
    raw = await client.get_async_httpx_client().request(
        method="get",
        url=f"/api/projects/{project}/merge-requests",
        params=params,
    )
    if raw.status_code == 401:
        raise PermissionError("Authentication failed: check user and access_key")
    if raw.status_code == 403:
        raise PermissionError("Access denied: the user does not have permission")
    if raw.status_code != 200:
        raise RuntimeError(f"Teamscale returned unexpected status {raw.status_code}")
    return raw.json().get("mergeRequests", [])


@MCP.tool()
@teamscale_tool
async def get_merge_request_finding_churn(
    project: str,
    source: str,
    target: str,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> dict:
    """Get the finding churn (added, removed, in changed code) for a merge request.

    source and target are commit descriptors, e.g. "feature-branch:HEAD" and "main:HEAD".
    Returns added findings, removed findings, findings in changed code, and a summary.
    """
    client = resolve_connection(server, user, access_key)
    response = await fetch(api_get_merge_request_finding_churn.asyncio_detailed(
        project=project,
        client=client,
        source=source,
        target=target,
    ))
    return response.parsed.to_dict()


@MCP.tool()
@teamscale_tool
async def pre_commit_upload(
    project: str,
    changes: str,
    branch: str | None = None,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> dict:
    """Upload file changes for pre-commit analysis and return immediate results.

    The changes parameter is a JSON string mapping file paths to their new content.
    Use null values for deleted files. Example: {"src/foo.py": "print('hi')", "old.py": null}
    Returns findings, an optional polling token, and any errors.
    """
    client = resolve_connection(server, user, access_key)
    body = RequestPreCommitAnalysisBody()
    body.additional_properties = json.loads(changes)
    response = await fetch(
        request_pre_commit_analysis.asyncio_detailed(
            project=project,
            client=client,
            body=body,
            branch=branch if branch is not None else UNSET,
        ),
        expect_body=False,
    )
    if response.parsed is not None:
        result = response.parsed
    else:
        try:
            result = PreCommit3Result.from_dict(json.loads(response.content))
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            raise RuntimeError(f"Failed to parse pre-commit response: {e}") from e
    return result.to_dict()


@MCP.tool()
@teamscale_tool
async def pre_commit_poll(
    project: str,
    token: str,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> dict:
    """Poll for pre-commit analysis results using a token from pre_commit_upload.

    Analysis is complete when the returned token field is absent or empty.
    """
    client = resolve_connection(server, user, access_key)
    response = await fetch(
        poll_pre_commit_results.asyncio_detailed(
            project=project,
            token=token,
            client=client,
        ),
    )
    return response.parsed.to_dict()


@MCP.tool()
@teamscale_tool
async def pre_commit_analyze(
    project: str,
    changes: str,
    branch: str | None = None,
    server: str | None = None,
    user: str | None = None,
    access_key: str | None = None,
    fetch: Callable[[Awaitable], Awaitable] | None = None,
) -> dict:
    """Upload file changes and poll until pre-commit analysis is complete.

    Combined tool: uploads changes, then polls every 2 seconds until analysis finishes.
    The changes parameter is a JSON string mapping file paths to their new content.
    Use null values for deleted files. Example: {"src/foo.py": "print('hi')", "old.py": null}
    Returns the final findings and any errors.
    """
    client = resolve_connection(server, user, access_key)
    body = RequestPreCommitAnalysisBody()
    body.additional_properties = json.loads(changes)
    response = await fetch(
        request_pre_commit_analysis.asyncio_detailed(
            project=project,
            client=client,
            body=body,
            branch=branch if branch is not None else UNSET,
        ),
        expect_body=False,
    )
    if response.parsed is not None:
        result = response.parsed
    else:
        try:
            result = PreCommit3Result.from_dict(json.loads(response.content))
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            raise RuntimeError(f"Failed to parse pre-commit response: {e}") from e

    while result.token is not UNSET and result.token:
        await asyncio.sleep(2)
        poll_response = await fetch(
            poll_pre_commit_results.asyncio_detailed(
                project=project,
                token=result.token,
                client=client,
            ),
        )
        result = poll_response.parsed

    return result.to_dict()


def main():
    MCP.run(transport="stdio")


if __name__ == "__main__":
    main()