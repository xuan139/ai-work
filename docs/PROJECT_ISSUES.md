# Project Issues

## 2026-10-10 — Enterprise evaluation baseline was not reproducible

- **Trigger:** The evaluation center had no standard employee identities or approved baseline cases, so permission and answer regression tests could not be run after deployment.
- **Root cause:** The first evaluation release provided the execution and review workflow but left test identity, department permission, source fixture, and case creation entirely manual.
- **Fix:** Add an idempotent administrator bootstrap that creates four reserved standard-employee identities, three department groups, sixteen traceable NAS source fixtures, and forty approved cases covering normal, cross-document, insufficient-evidence, cross-department, and version scenarios.
- **Verification:** Run the bootstrap twice and confirm that identity, group, source, and case counts remain stable; verify representative company, department, and private source permissions; run the targeted and full automated test suites.
- **Not yet verified:** Final-answer quality against every case depends on the configured production LLM and must be reviewed through the evaluation center after deployment. The independent judge model is intentionally not part of this phase.
- **Rollback:** Restore the pre-deployment application and SQLite backup. The seeded rows are isolated by `eval.*` usernames, `evaluation_fixture` source type, `evaluation://enterprise-baseline-v1/*` source URLs, dedicated group names, and the `enterprise-baseline-v1` suite marker.
