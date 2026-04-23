# Teamscale OpenAPI Plugin for Claude Code

A [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code) that exposes the [Teamscale](https://teamscale.com) REST API as MCP resources and tools, auto-generated from the Teamscale OpenAPI spec.

GET endpoints are exposed as MCP resources (or resource templates when they contain path parameters). Non-GET endpoints (POST, PUT, DELETE, etc.) are excluded by default. Set the `ENABLE_TOOLS` environment variable to expose them as MCP tools.

Unlike the [custom plugin](../teamscale-python-custom/), which provides hand-crafted higher-level tools, this plugin exposes the full Teamscale REST API surface automatically.

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager
- A Teamscale instance with API access
- A Teamscale access key (generate one in your Teamscale user profile)

## Installation

This plugin is distributed via the [teamscale-claude-marketplace](../../). See the [marketplace README](../../README.md) for installation, standalone setup, and debug instructions.

## Configuration

The plugin requires the following environment variables:

| Variable | Description |
|---|---|
| `TEAMSCALE_URL` | URL of the Teamscale instance (e.g. `https://myinstance.teamscale.io`) |
| `TEAMSCALE_USER` | Your Teamscale username |
| `TEAMSCALE_ACCESS_KEY` | Your Teamscale access key |
| `ENABLE_TOOLS` | Set to expose non-GET endpoints as MCP tools (optional) |

## Available Resources and Resource Templates

Resources are read-only GET endpoints; resource templates require path parameters.

### Resources

| Category | Resource | Description |
|---|---|---|
| API | `getApiVersion` | Service API version info |
| Backup | `getBackupExportSummary` | Summary of the 10 most recent backup exports |
| Backup | `getBackupImportSummary` | Summary of the 10 most recent backup imports |
| Dashboards | `getDashboardThumbnail` | Jira dashboard gadget thumbnail |
| Dashboards | `getDashboardGadget` | XML descriptor for the dashboard gadget |
| Monitoring | `getHealthStatus` | System health status log |
| Pre-Commit | `getPreCommitServerLimits` | Configured limits for pre-commit analysis |
| Project | `getAllProjects` | List of all visible projects |
| Project | `getAllProjectIds` | All primary project IDs |
| SAP | `getAllSapSystemConnectionIdentifiers` | SAP connection identifiers |
| Users | `getAllUsers` | List of all visible users |

### Resource Templates

Resource templates are parameterized endpoints. Path parameters like `{project}` or `{findingId}` must be provided when reading the resource.

| Category | Resource Template | Path | Description |
|---|---|---|---|
| Architecture | `getAllArchitectureAssessments` | `/projects/{project}/architectures/assessments` | Get all architecture assessments |
| Backup | `downloadBackup` | `/backups/export/{backupId}/download` | Download backup |
| Backup | `getBackupExportStatus` | `/backups/export/{backupId}/status` | Get the backup export status |
| Backup | `getBackupImportStatus` | `/backups/import/{backupId}/status` | Get the backup import status |
| Baselines | `getAllBaselines` | `/projects/{project}/baselines` | Get all baselines |
| Baselines | `getBaseline` | `/projects/{project}/baselines/{baseline}` | Get baseline |
| Connectors | `getCommitsForRevision` | `/projects/{project}/revision/{revision}/commits` | Get Teamscale commits |
| Debugging | `dumpLogsAndReports` | `/projects/{project}/sap-test-event/dump-logs-and-reports` | Returns SAP server log and status info for a recorded test |
| Delta | `getDeltaAffectedFiles` | `/projects/{project}/delta/affected-files` | Get token element churn |
| Delta | `getSpecItemChurn` | `/projects/{project}/delta/affected-spec-items` | Get spec item churn |
| Findings | `getFindings` | `/projects/{project}/findings/list` | Get findings |
| Findings | `getFindingsWithCount` | `/projects/{project}/findings/list/with-count` | Get findings with false positive counts |
| Findings | `getFinding` | `/projects/{project}/findings/{id}` | Get finding |
| Findings | `getFindingWithDiffInfo` | `/projects/{project}/findings/{id}/with-diff-info` | Get finding with diff information |
| Findings | `getFindingChurnList` | `/projects/{project}/finding-churn/list` | Get finding churn list |
| Findings | `getFindingDueDate` | `/projects/{project}/external-properties/findings/{findingId}/due-date` | Get due date |
| Findings | `getFindingGenericProperties` | `/projects/{project}/external-properties/findings/{findingId}/properties` | Get generic external properties |
| Findings | `getFindingDeltaBadge` | `/projects/{project}/findings/delta/badge` | Get finding delta badge |
| Findings (SAP) | `getAbapFindings` | `/projects/{project}/findings/abap` | Get all ABAP findings |
| Findings (SAP) | `getAbapFindings` | `/projects/{project}/findings/abap/{objectType}/{objectName}` | Get ABAP findings |
| Issues | `getIssueFindingChurn` | `/projects/{project}/issues/{issueId}/finding-churn` | Get issue finding churn |
| Issues | `getIssueFindingBadge` | `/projects/{project}/issues/{issueId}/findings-badge` | Get issue finding badge |
| Merge Requests | `getMergeRequestTestSuggestions` | `/projects/{project}/merge-requests/test-suggestions` | Get merge request impacted tests |
| Metrics | `getResourceType` | `/projects/{project}/resource-type` | Get resource type |
| Pre-Commit | `pollPreCommitResults` | `/projects/{project}/pre-commit/{token}` | Poll for pre-commit analysis results |
| Pre-Commit | `pollLegacyPreCommit3Results` | `/projects/{project}/pre-commit3/{token}` | Poll pre-commit 3.0 results |
| Project | `getProject` | `/projects/{project}` | Get project |
| Project | `getBranchesGetRequest` | `/projects/{project}/branches` | Get branches |
| Project | `getProjectConfiguration` | `/projects/{project}/configuration` | Get project configuration |
| Project | `getProjectProperties` | `/projects/{project}/configuration/properties` | Get project properties |
| Project | `getFirstUIBranchNameForProject` | `/projects/{project}/default-branch` | Get the default branch for the UI |
| Project | `getLanguages` | `/projects/{project}/languages` | Get project languages |
| Project | `exportTeamscaleToml` | `/projects/{project}/teamscale-toml` | Export a Teamscale IDE configuration file |
| Project | `areAbapProjectsUpdating` | `/sap-sysid-projects/{sysid}/is-updating/{updateid}` | Check if ABAP projects are synchronizing |
| SAP | `lookupProjectBySapSystemId` | `/projects-by-sap-system-id/{sapSystemId}` | Get projects for a SAP system ID |
| SAP | `lookupSapSystemIdByProjectId` | `/sap-system-id-by-project/{projectId}` | Get SAP system ID for a project |
| Software Composition | `getViolationDueDate` | `/projects/{project}/external-properties/violations/{violationId}/due-date` | Get due date |
| Software Composition | `getViolationGenericProperties` | `/projects/{project}/external-properties/violations/{violationId}/properties` | Get generic external properties |
| Source Code | `getCode` | `/projects/{project}/source-code-download/{uniformPath}` | Download source code |
| Test Coverage | `getLogInformation` | `/projects/{project}/sap-test-event/log/{sapTestKey}` | Return SAP server log for a recorded test |
| Test Coverage | `getLineCoveragePartitionsForPath` | `/projects/{project}/test-coverage-partitions/{uniformPath}` | Line coverage partitions |
| Test Gap Analysis | `getTgaPercentage` | `/projects/{project}/test-gaps/percentage` | Get test gap percentage |
| Test Gap Analysis | `getIssueTgaSummary` | `/projects/{project}/issues/{issueId}/tga-summary` | Get TGA summary |
| Test Intelligence | `getImpactedTests` | `/projects/{project}/impacted-tests` | Get impacted tests |
| Test Intelligence | `getMinimizedTests` | `/projects/{project}/minimized-tests` | Get minimized test set |
| Users | `getUser` | `/users/{user}` | Get user |

### Tools

When `ENABLE_TOOLS` is set, the plugin additionally exposes the following MCP tools (non-GET endpoints). These are write/mutate operations that require appropriate Teamscale permissions.

| Category | Tool | Description |
|---|---|---|
| Authentication | `authenticateWithPasswordOrAccessKey` | Authenticate with password or access key and generate a new access key |
| Backup | `createBackup` | Trigger creation of a backup |
| Backup | `importBackup` | Import a backup |
| Backup | `importBackupFromRemote` | Import a backup from a remote instance |
| Baselines | `createOrUpdateBaseline` | Create or update a baseline |
| Baselines | `deleteBaseline` | Delete a baseline |
| Branches | `getBranchesPostRequest` | Get branches with filtering and pagination |
| Dashboards | `importDashboard` | Import a dashboard |
| Dashboards | `importAndReplaceDashboards` | Import and replace existing dashboards |
| External Analysis | `createSession` | Create an upload session |
| External Analysis | `commitAnalysisResults` | Commit and close an upload session |
| External Analysis | `deleteAnalysisResults` | Abort/delete an upload session |
| External Analysis | `addExternalMetrics` | Add external metrics to the schema |
| External Analysis | `createExternalAnalysisGroup` | Create an external analysis group |
| External Analysis | `createExternalFindingDescription` | Create an external finding description |
| External Analysis | `uploadExternalAnalysisResults` | Upload external analysis results to a session |
| External Analysis | `uploadExternalFindings` | Upload external findings to a session |
| External Analysis | `uploadExternalMetrics` | Upload external metrics to a session |
| External Analysis | `uploadNonCodeMetrics` | Upload non-code metrics to a session |
| External Analysis | `uploadReport` | Upload external reports (JaCoCo, Cobertura, JUnit, etc.) |
| External Analysis | `uploadDebugInfo` | Upload PDB/MDB debug info for .NET |
| External Analysis | `uploadDotNetTrace` | Upload .NET profiler coverage trace |
| External Analysis | `uploadArchitecture` | Import an architecture file |
| Findings | `flagFindings` | Flag/unflag findings (false positive, toleration) |
| Findings | `getFindingsWithIds` | Get findings by their IDs |
| Findings | `getFindingTypeDescriptions` | Get finding type names and descriptions |
| Findings | `setFindingDueDate` | Set due date for a finding |
| Findings | `setFindingDueDates` | Set due dates for multiple findings |
| Findings | `deleteFindingDueDate` | Delete due date for a finding |
| Findings | `setFindingGenericProperties` | Set external properties for a finding |
| Findings | `setMultipleFindingGenericProperties` | Set properties for multiple findings |
| Findings | `deleteFindingGenericProperties` | Delete external properties for a finding |
| Issues | `saveIssueQueryDescriptor` | Create an issue query |
| Pre-Commit | `requestPreCommitAnalysis` | Upload changes and run pre-commit analysis |
| Pre-Commit | `requestLegacyPreCommit3Analysis` | Upload changes and run legacy pre-commit 3.0 analysis |
| Pre-Commit | `deletePreCommitBranch` | Remove pre-commit branch data |
| Pre-Commit | `clearLegacyPreCommit3Branch` | Remove legacy pre-commit 3.0 branch data |
| Profiler | `registerProfiler` | Register a profiler and get its configuration |
| Profiler | `unregisterProfiler` | Unregister a profiler |
| Profiler | `receiveHeartbeat` | Update profiler heartbeat and info |
| Profiler | `postProfilerLog` | Push profiler logs |
| Project | `createProject` | Create a new project from configuration |
| Project | `editProject` | Update an existing project |
| Project | `editProjectWithConfiguration` | Edit project with full configuration |
| Project | `deleteProject` | Delete a project |
| Project | `updateProjectProperties` | Update project properties (no re-analysis needed) |
| Project | `triggerReanalysis` | Trigger project reanalysis |
| Project | `calculateProjectMappings` | Calculate path prefix mappings for a project |
| SAP | `synchronizeAbapProjects` | Incrementally synchronize ABAP projects |
| SAP | `startTest` | Start SAP coverage recording for a test |
| SAP | `stopTest` | Stop SAP coverage recording for a test |
| SAP | `pauseTest` | Pause SAP test and update its info |
| SAP | `updateTest` | Update info for a running SAP test |
| SAP | `resetRecordingState` | Reset SAP coverage recording state |
| Software Composition | `setViolationDueDate` | Set due date for a violation |
| Software Composition | `setViolationDueDates` | Set due dates for multiple violations |
| Software Composition | `deleteViolationDueDate` | Delete due date for a violation |
| Software Composition | `setViolationGenericProperties` | Set properties for multiple violations (batch) |
| Software Composition | `setViolationGenericProperties_1` | Set properties for a single violation |
| Software Composition | `deleteViolationGenericProperties` | Delete properties for a violation |
| Test Intelligence | `getImpactedTestsFromAvailableTests` | Get prioritized impacted tests from available test list |
| Users | `putUser` | Create or update a user |
| Users | `deleteUser` | Delete one or more users |
| Users | `deleteUsers` | Delete users (batch operation) |

## Plugin structure

```
.claude-plugin/plugin.json   Plugin manifest — declares the MCP servers
server/                      MCP server (Python, FastMCP + OpenAPI provider)
```
