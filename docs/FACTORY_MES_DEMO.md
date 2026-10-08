# FactorySemantics MES demo

The simulated bottling plant and the AI Work read-only MCP run as separate
systemd services on Ubuntu. Neither port is published through Nginx:

- FactorySemantics plant API: `127.0.0.1:8010`
- AI Work MES MCP: `127.0.0.1:8310/mcp`

The plant is based on the upstream FactorySemantics MES bottling pack. Pin the
checkout to the tested commit before installation; do not track its data or
credentials in the AI Work repository.

1. Install the upstream `factorysemantics-mes[mcp]` package into a separate
   `/home/ubuntu/factory-mes-venv` Python 3.12 environment and initialize the
   bottling pack with `fsmes plant bottling init`.
2. Generate `MES_SECRET_KEY`, `MES_ADMIN_PASSWORD`, `FSMES_AGENT_PASSWORD`, and
   `FSMES_ANALYST_PASSWORD` in `/home/ubuntu/.config/ai-work-mes/env` (mode 600).
   Both services use the same analyst password. Keep the file out of Git.
3. Install `deploy/factory-mes-plant.service` and
   `deploy/factory-mes-mcp.service` under `/etc/systemd/system/`, then enable
   and start them in that order.
4. Confirm `ss -ltn` shows ports 8010 and 8310 only on `127.0.0.1`, and
   `curl http://127.0.0.1:8010/health` reports plant `bottling`.
5. In AI Work MCP management, enable and sync `FactorySemantics MES 唯讀`.
   Then select that MCP server in AI Work and use one of its three sample
   questions.

The MCP adapter authenticates to the plant as `ANALYST`, whose role is limited
to `plant.read` and `audit.read`. It only issues GET requests after login and
exposes three tools: overdue work orders, today's downtime, and one work
order's production/quality history. AI Work also rejects any tool name outside
this fixed list. An empty result means the simulated line has not recorded
matching events; it is not evidence that a real factory had none.

Upstream: https://github.com/factorysemantics/factorysemantics-mes
