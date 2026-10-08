"""Three read-only MES tools. Run only on the Ubuntu loopback interface."""

from __future__ import annotations

import os

import anyio
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

from app.mes_readonly import MesReader


reader = MesReader(
    os.getenv("MES_READONLY_API_URL", "http://127.0.0.1:8010"),
    os.getenv("FSMES_ANALYST_PASSWORD", ""),
)
mcp = MCPServer(name="AI Work MES Read-only")


@mcp.tool()
def mes_overdue_orders() -> dict:
    """List open FactorySemantics MES work orders with due dates before now."""
    return reader.overdue_orders()


@mcp.tool()
def mes_line_downtime_today() -> dict:
    """Explain today's recorded line downtime and current machine states in the plant time zone."""
    return reader.line_downtime_today()


@mcp.tool()
def mes_work_order_production_quality(code: str) -> dict:
    """Read one MES work order, material genealogy and its matching quality checks."""
    return reader.work_order_production_quality(code)


def main() -> None:
    security = TransportSecuritySettings(
        allowed_hosts=["127.0.0.1", "127.0.0.1:8310", "localhost", "localhost:8310"],
        allowed_origins=["http://127.0.0.1:8310"],
    )
    anyio.run(lambda: mcp.run_streamable_http_async(
        host="127.0.0.1", port=8310, transport_security=security
    ))


if __name__ == "__main__":
    main()
