# OR-Tools CP-SAT scheduling comparison

## Trigger

The manufacturing scheduling demo used one deterministic finite-capacity rule engine, so it could not demonstrate whether a constraint solver reduced lateness and changeovers on the same MCP snapshot.

## Implementation

- Keep `finite-capacity-mcp-v4` as the default and fallback engine.
- Add optional `ortools-cp-sat-v1` scheduling with job precedence, finite work-center capacity, shifts, downtime, material availability, maintenance, quality/SPC time, and sequence-dependent changeovers.
- Run both engines from the same immutable MCP snapshot and show their metrics and Gantt schedules side by side.
- Compute the comparison verdict and deltas in the backend. The LLM receives these values as evidence and must not recalculate them.
- Allow an administrator to select OR-Tools as the system default only after it is available and improves weighted lateness or changeover without making either metric worse.
- If OR-Tools is missing or cannot produce a feasible result, continue with the rule engine.

## Verification

- All 254 Python tests pass locally; one optional OR-Tools test is skipped under local Python 3.14 because no compatible wheel is available.
- The real CP-SAT test passes in an isolated Python 3.12 environment with OR-Tools 9.15.6755.
- The browser test passes at desktop and mobile widths with both metric sets and Gantt charts visible.
- Production Python 3.12 reports an `OPTIMAL` solution. In the validated rush-order, two-hour SMT downtime scenario, CP-SAT reduced weighted late minutes by 6,392, changeover minutes by 65, and makespan by 375 minutes.
- Production LLM output uses the backend verdict and remained within the 4,096-token local-model context limit.

## Unverified

- The comparison is a demo result, not proof that CP-SAT dominates every future production dataset.
- Solver weights and the three-second time limit require calibration against approved business KPIs and larger real order sets.
- Existing SQLite `ResourceWarning` messages from the full suite are unrelated and remain unresolved.

## Rollback

Set `current_scheduling_engine_id` back to `finite-capacity-mcp-v4`, remove the optional OR-Tools package, restore the previous manufacturing demo files, and restart the service. MCP data and existing audit records do not require a database rollback.

## 2026-10-19 professional console UI

- **Trigger:** The scheduling demo exposed all data but read as one long technical report, with the summary below the controls and every connected-system detail expanded.
- **Root cause:** Controls, decisions, results, and supporting evidence had similar visual weight, so users could not quickly identify the current risk, run a scenario, or compare engines.
- **Fix:** Reorder the page as status and KPIs, scenario/AI workbench, dual-engine decision, schedule output, and system evidence. Add section navigation, stronger risk/status hierarchy, paired engine panels, responsive control layouts, and collapsible QMS/CMMS/WMS/PLM/SPC evidence. Keep the two most operational inputs, MES capacity and inventory, expanded by default. No scheduling or MCP behavior changed.
- **Verification:** JavaScript syntax and the Chrome fixture suite pass. The suite checks the new structure, collapsed/open defaults, all prior interactions, and no horizontal overflow at 1440 px and 390 px. Desktop and mobile screenshots were inspected.
- **Deployment:** Backed up the prior static files at `/home/ubuntu/ai-work/backups/manufacturing-ui-20261019-084651`, then replaced only the manufacturing HTML, CSS, and JavaScript. No service restart or database change was required. All three deployed file hashes match local files, public CSS/JavaScript hashes match the release, and the protected page continues to return 401 to an anonymous request.
- **Unverified:** Final typography depends on the client operating system's available Traditional Chinese font. Authenticated production-browser behavior remains to be checked after deployment.
- **Rollback:** Restore the previous manufacturing schedule HTML, CSS, JavaScript, and UI test. Backend data, settings, jobs, and the OR-Tools installation are unaffected.
