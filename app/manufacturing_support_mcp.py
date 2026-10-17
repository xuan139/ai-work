"""Loopback-only read-only QMS and CMMS MCP for the manufacturing demo."""

from __future__ import annotations

import anyio
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

from app.manufacturing_extension_demo import (
    change_impact,
    current_bom,
    engineering_snapshot,
    lot_location,
    material_availability,
    open_ecos,
    order_genealogy,
    order_quality_risk,
    out_of_control_points,
    process_capability,
    process_snapshot,
    product_revision,
    recall_impact,
    revision_difference,
    serial_history,
    warehouse_snapshot,
)
from app.manufacturing_support_demo import (
    maintenance_asset_detail,
    maintenance_snapshot,
    quality_order_detail,
    quality_snapshot,
)


qms_mcp = MCPServer(name="AI Work QMS Demo Read-only")
cmms_mcp = MCPServer(name="AI Work CMMS Demo Read-only")
wms_mcp = MCPServer(name="AI Work WMS Traceability Demo Read-only")
plm_mcp = MCPServer(name="AI Work PLM ECO Demo Read-only")
spc_mcp = MCPServer(name="AI Work SPC Demo Read-only")


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


@wms_mcp.tool()
def wms_inventory_snapshot() -> dict:
    """Return synthetic warehouse locations, lots, availability, and serial genealogy."""
    return warehouse_snapshot()


@wms_mcp.tool()
def wms_material_availability(family: str, quantity: float) -> dict:
    """Read material availability and ready time for one teaching product family."""
    return material_availability(family, quantity)


@wms_mcp.tool()
def wms_lot_location(lot_id: str) -> dict:
    """Read the location and status of one teaching lot."""
    return lot_location(lot_id)


@wms_mcp.tool()
def trace_serial_history(serial: str) -> dict:
    """Read a teaching finished-product serial genealogy record."""
    return serial_history(serial)


@wms_mcp.tool()
def trace_order_genealogy(order: str) -> dict:
    """Read serial and consumed-lot genealogy for one teaching order."""
    return order_genealogy(order)


@wms_mcp.tool()
def trace_recall_impact(lot_id: str) -> dict:
    """Read teaching serials and orders affected by one lot."""
    return recall_impact(lot_id)


@plm_mcp.tool()
def plm_engineering_snapshot() -> dict:
    """Return synthetic released BOM revisions and engineering changes for scheduling."""
    return engineering_snapshot()


@plm_mcp.tool()
def plm_current_bom(family: str) -> dict:
    """Read the current teaching BOM for one product family."""
    return current_bom(family)


@plm_mcp.tool()
def plm_product_revision(family: str) -> dict:
    """Read the released teaching product revision for one family."""
    return product_revision(family)


@plm_mcp.tool()
def plm_open_ecos() -> dict:
    """List open teaching engineering change orders."""
    return open_ecos()


@plm_mcp.tool()
def plm_revision_difference(eco_id: str) -> dict:
    """Read the bounded revision difference for one teaching ECO."""
    return revision_difference(eco_id)


@plm_mcp.tool()
def plm_change_impact(eco_id: str) -> dict:
    """Read schedule and order impact for one teaching ECO."""
    return change_impact(eco_id)


@spc_mcp.tool()
def spc_process_snapshot() -> dict:
    """Return synthetic process capability and out-of-control points for scheduling."""
    return process_snapshot()


@spc_mcp.tool()
def spc_process_capability(family: str) -> dict:
    """Read Cp/Cpk and control status for one teaching product family."""
    return process_capability(family)


@spc_mcp.tool()
def spc_out_of_control_points() -> dict:
    """List bounded teaching SPC out-of-control points."""
    return out_of_control_points()


@spc_mcp.tool()
def spc_quality_risk_by_order(order: str, family: str, quantity: float) -> dict:
    """Estimate teaching inspection time for an order from SPC capability."""
    return order_quality_risk(order, family, quantity)


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


async def _run_wms() -> None:
    security = TransportSecuritySettings(
        allowed_hosts=["127.0.0.1", "127.0.0.1:8322", "localhost", "localhost:8322"],
        allowed_origins=["http://127.0.0.1:8322"],
    )
    await wms_mcp.run_streamable_http_async(
        host="127.0.0.1", port=8322, transport_security=security
    )


async def _run_plm() -> None:
    security = TransportSecuritySettings(
        allowed_hosts=["127.0.0.1", "127.0.0.1:8323", "localhost", "localhost:8323"],
        allowed_origins=["http://127.0.0.1:8323"],
    )
    await plm_mcp.run_streamable_http_async(
        host="127.0.0.1", port=8323, transport_security=security
    )


async def _run_spc() -> None:
    security = TransportSecuritySettings(
        allowed_hosts=["127.0.0.1", "127.0.0.1:8324", "localhost", "localhost:8324"],
        allowed_origins=["http://127.0.0.1:8324"],
    )
    await spc_mcp.run_streamable_http_async(
        host="127.0.0.1", port=8324, transport_security=security
    )


async def _run_servers() -> None:
    async with anyio.create_task_group() as group:
        group.start_soon(_run_qms)
        group.start_soon(_run_cmms)
        group.start_soon(_run_wms)
        group.start_soon(_run_plm)
        group.start_soon(_run_spc)


def main() -> None:
    anyio.run(_run_servers)


if __name__ == "__main__":
    main()
