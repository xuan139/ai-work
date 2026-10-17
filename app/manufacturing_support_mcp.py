"""Loopback-only read-only QMS and CMMS MCP for the manufacturing demo."""

from __future__ import annotations

import anyio
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

from app.manufacturing_support_demo import (
    maintenance_asset_detail,
    maintenance_snapshot,
    quality_order_detail,
    quality_snapshot,
)


qms_mcp = MCPServer(name="AI Work QMS Demo Read-only")
cmms_mcp = MCPServer(name="AI Work CMMS Demo Read-only")


@qms_mcp.tool()
def qms_quality_snapshot() -> dict:
    """Return synthetic electronics quality profiles and open quality events for scheduling."""
    return quality_snapshot()


@qms_mcp.tool()
def qms_order_quality(order: str, family: str, quantity: float) -> dict:
    """Estimate teaching-demo rework time for one order from its product-family quality profile."""
    return quality_order_detail(order, family, quantity)


@cmms_mcp.tool()
def cmms_maintenance_snapshot() -> dict:
    """Return synthetic equipment health and planned maintenance windows for scheduling."""
    return maintenance_snapshot()


@cmms_mcp.tool()
def cmms_asset_maintenance(center_id: str) -> dict:
    """Read the teaching maintenance record for one manufacturing work center."""
    return maintenance_asset_detail(center_id)


async def _run_qms() -> None:
    security = TransportSecuritySettings(
        allowed_hosts=["127.0.0.1", "127.0.0.1:8320", "localhost", "localhost:8320"],
        allowed_origins=["http://127.0.0.1:8320"],
    )
    await qms_mcp.run_streamable_http_async(
        host="127.0.0.1", port=8320, transport_security=security
    )


async def _run_cmms() -> None:
    security = TransportSecuritySettings(
        allowed_hosts=["127.0.0.1", "127.0.0.1:8321", "localhost", "localhost:8321"],
        allowed_origins=["http://127.0.0.1:8321"],
    )
    await cmms_mcp.run_streamable_http_async(
        host="127.0.0.1", port=8321, transport_security=security
    )


async def _run_servers() -> None:
    async with anyio.create_task_group() as group:
        group.start_soon(_run_qms)
        group.start_soon(_run_cmms)


def main() -> None:
    anyio.run(_run_servers)


if __name__ == "__main__":
    main()
