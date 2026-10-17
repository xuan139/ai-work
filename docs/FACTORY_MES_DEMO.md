# FactorySemantics MES demo

The simulated bottling plant and the AI Work read-only MCP run as separate
systemd services on Ubuntu. Neither port is published through Nginx:

- FactorySemantics plant API: `127.0.0.1:8010`
- AI Work MES MCP: `127.0.0.1:8310/mcp`
- AI Work QMS Demo MCP: `127.0.0.1:8320/mcp`
- AI Work CMMS Demo MCP: `127.0.0.1:8321/mcp`

The plant is based on the upstream FactorySemantics MES bottling pack, tested
at commit `d8d077dcaeb111fdbb4f26745354e9898544f293`. Pin that checkout
before installation; do not track its data or credentials in the AI Work
repository.

1. Install the upstream `factorysemantics-mes[mcp]` package into a separate
   `/home/ubuntu/factory-mes-venv` Python 3.12 environment and initialize the
   bottling pack with `fsmes plant bottling init`. In the upstream checkout,
   run `fsmes sim-generate labs/kepsim/line.json` before starting the plant;
   the pack needs the generated replay CSVs.
2. Generate `MES_SECRET_KEY`, `MES_ADMIN_PASSWORD`, `FSMES_AGENT_PASSWORD`, and
   `FSMES_ANALYST_PASSWORD` in `/home/ubuntu/.config/ai-work-mes/env` (mode 600).
   Both services use the same analyst password. Keep the file out of Git.
   The upstream lab pack creates a default `ADMIN` password; change it with
   `fsmes set-password ADMIN` against the bottling database before offering
   the demo to users. Do not proxy the plant API or MCP to the public internet.
3. Install `deploy/factory-mes-plant.service` and
   `deploy/factory-mes-mcp.service` under `/etc/systemd/system/`, then enable
   and start them in that order. Install and enable
   `deploy/manufacturing-support-mcp.service` for the independent synthetic
   QMS/CMMS teaching adapter.
4. Confirm `ss -ltn` shows ports 8010, 8310, 8320 and 8321 only on `127.0.0.1`, and
   `curl http://127.0.0.1:8010/health` reports plant `bottling`.
5. In AI Work MCP management, enable and sync `FactorySemantics MES 唯讀`.
   Then select that MCP server in AI Work and use one of its sample questions.
   The included pack has work order `WO-ACME-4711`; the deployed
   demo also contains `WO-DEMO-LATE-001`, created with a past due date through
   the local plant API so the overdue-order question has one real example.

The MCP adapter authenticates to the plant as `ANALYST`, whose role is limited
to `plant.read` and `audit.read`. It only issues GET requests after login and
exposes four tools: overdue work orders, today's downtime, one work
order's production/quality history, and an explicitly synthetic electronics
work-center snapshot for the scheduling demo. AI Work also rejects any tool name outside
this fixed list. An empty result means the simulated line has not recorded
matching events; it is not evidence that a real factory had none.

The QMS and CMMS catalog entries use separate loopback endpoints in one
restricted systemd process. QMS exposes `qms_quality_snapshot` and
`qms_order_quality`; CMMS exposes `cmms_maintenance_snapshot` and
`cmms_asset_maintenance`. All records are authored teaching data. The
scheduling demo uses expected family rework time in the TEST operation and
uses CMMS maintenance windows as unavailable capacity. It cannot release a
lot, close a quality event, acknowledge an alarm, or update a maintenance work
order. If either connector is disabled or unavailable, scheduling returns an
explicit error instead of silently substituting process-local fixtures.

Upstream: https://github.com/factorysemantics/factorysemantics-mes
