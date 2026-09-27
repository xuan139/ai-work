from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


PROTOCOL_VERSION = "2025-06-18"
DEFAULT_TIMEOUT_SECONDS = 15
MAX_OUTPUT_CHARS = 512 * 1024
DEVICE_PATTERN = re.compile(r"^/dev/(?:nvme\d+n\d+|sd[a-z]+|vd[a-z]+)$")

SSD_MCP_TOOLS = [
    {
        "name": "ssd_list_devices",
        "title": "List SSD Devices",
        "description": "List physical SSD and NVMe devices detected by the NAS without modifying them.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "ssd_get_usage",
        "title": "Get SSD Filesystem Usage",
        "description": "Return filesystem capacity and usage for mounted filesystems backed by detected SSD devices.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "ssd_get_health",
        "title": "Get SSD SMART Health",
        "description": (
            "Read SMART or NVMe health, temperature, wear, power-on hours, and media errors for one detected SSD. "
            "The device must come from ssd_list_devices."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "device": {
                    "type": "string",
                    "description": "Detected whole-device path such as /dev/nvme0n1 or /dev/sda.",
                    "pattern": r"^/dev/(nvme\d+n\d+|sd[a-z]+|vd[a-z]+)$",
                }
            },
            "required": ["device"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
]


class SsdCliError(RuntimeError):
    pass


def handle_ssd_mcp_request(payload: dict[str, Any]) -> dict[str, Any] | None:
    method = str(payload.get("method") or "")
    request_id = payload.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return _result(
            request_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "AI Work NAS SSD CLI MCP", "version": "1.0.0"},
                "instructions": (
                    "Read-only SSD inventory, filesystem usage, and SMART/NVMe health. "
                    "Arbitrary commands, writes, tests, formatting, and firmware operations are not supported."
                ),
            },
        )
    if method == "ping":
        return _result(request_id, {})
    if method == "tools/list":
        return _result(request_id, {"tools": SSD_MCP_TOOLS})
    if method == "tools/call":
        params = payload.get("params") if isinstance(payload.get("params"), dict) else {}
        name = str(params.get("name") or "")
        arguments = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
        try:
            output = _call_tool(name, arguments)
        except (ValueError, SsdCliError) as exc:
            return _error(request_id, -32602, str(exc))
        return _result(
            request_id,
            {
                "content": [{"type": "text", "text": json.dumps(output, ensure_ascii=False)}],
                "structuredContent": output,
                "isError": False,
            },
        )
    return _error(request_id, -32601, f"Method not found: {method}")


def _call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "ssd_list_devices":
        devices, _ = _ssd_inventory()
        return {"read_only": True, "count": len(devices), "devices": devices}
    if name == "ssd_get_usage":
        devices, paths = _ssd_inventory()
        filesystems = _filesystem_usage(paths)
        return {
            "read_only": True,
            "device_count": len(devices),
            "filesystem_count": len(filesystems),
            "filesystems": filesystems,
        }
    if name == "ssd_get_health":
        device = str(arguments.get("device") or "").strip()
        if not DEVICE_PATTERN.fullmatch(device):
            raise ValueError("device must be a whole SSD path returned by ssd_list_devices")
        devices, _ = _ssd_inventory()
        detected = {str(item["path"]): item for item in devices}
        if device not in detected:
            raise ValueError("device is not a detected SSD")
        return _ssd_health(device, detected[device])
    raise ValueError(f"Unknown tool: {name}")


def _ssd_inventory() -> tuple[list[dict[str, Any]], set[str]]:
    payload = _run_json(
        [
            "lsblk",
            "--json",
            "--bytes",
            "--output",
            "NAME,PATH,TYPE,SIZE,MODEL,SERIAL,ROTA,TRAN,FSTYPE,MOUNTPOINTS",
        ]
    )
    roots = payload.get("blockdevices") if isinstance(payload, dict) else None
    if not isinstance(roots, list):
        raise SsdCliError("lsblk did not return a block device list")

    devices: list[dict[str, Any]] = []
    all_paths: set[str] = set()
    for root in roots:
        if not isinstance(root, dict) or root.get("type") != "disk" or not _is_ssd(root):
            continue
        paths = _collect_paths(root)
        all_paths.update(paths)
        devices.append(
            {
                "name": root.get("name"),
                "path": root.get("path"),
                "size_bytes": _as_int(root.get("size")),
                "model": _clean(root.get("model")),
                "serial": _clean(root.get("serial")),
                "transport": _clean(root.get("tran")),
                "rotational": False,
                "partitions": _partition_summary(root.get("children")),
            }
        )
    devices.sort(key=lambda item: str(item.get("path") or ""))
    return devices, all_paths


def _filesystem_usage(ssd_paths: set[str]) -> list[dict[str, Any]]:
    completed = _run_command(
        ["df", "--block-size=1", "--output=source,fstype,size,used,avail,pcent,target"],
        check=True,
    )
    filesystems: list[dict[str, Any]] = []
    for line in completed.stdout.splitlines()[1:]:
        parts = line.split(None, 6)
        if len(parts) != 7 or parts[0] not in ssd_paths:
            continue
        source, fstype, size, used, available, percent, target = parts
        filesystems.append(
            {
                "source": source,
                "filesystem": fstype,
                "size_bytes": _as_int(size),
                "used_bytes": _as_int(used),
                "available_bytes": _as_int(available),
                "used_percent": _as_int(percent.rstrip("%")),
                "mountpoint": target,
            }
        )
    return filesystems


def _ssd_health(device: str, inventory: dict[str, Any]) -> dict[str, Any]:
    command = _health_command(device)
    if command is None:
        return {
            "read_only": True,
            "device": device,
            "available": False,
            "reason": "smartctl and nvme-cli are not installed",
            "install_hint": "Install smartmontools and nvme-cli on the NAS host.",
        }
    completed = _run_command(command, check=False)
    payload = _load_json(completed.stdout)
    if payload is None:
        message = (completed.stderr or completed.stdout).strip()[-2000:]
        return {
            "read_only": True,
            "device": device,
            "available": False,
            "tool": Path(command[-3] if command[0] == "sudo" else command[0]).name,
            "exit_code": completed.returncode,
            "reason": message or "SSD health command returned no JSON",
        }
    if "smartctl" in payload:
        return _smartctl_summary(device, inventory, payload, completed.returncode)
    return _nvme_summary(device, inventory, payload, completed.returncode)


def _health_command(device: str) -> list[str] | None:
    helper = os.getenv("SSD_CLI_HELPER", "").strip()
    if helper:
        helper_path = Path(helper)
        if helper_path.is_absolute() and helper_path.is_file():
            return ["sudo", "-n", str(helper_path), "health", device]
    if shutil.which("smartctl"):
        return ["smartctl", "-a", "-j", device]
    if device.startswith("/dev/nvme") and shutil.which("nvme"):
        return ["nvme", "smart-log", "-o", "json", device]
    return None


def _smartctl_summary(
    device: str,
    inventory: dict[str, Any],
    payload: dict[str, Any],
    exit_code: int,
) -> dict[str, Any]:
    nvme = payload.get("nvme_smart_health_information_log") or {}
    temperature = payload.get("temperature") or {}
    power_on = payload.get("power_on_time") or {}
    smart_status = payload.get("smart_status") or {}
    messages = payload.get("smartctl", {}).get("messages") or []
    return {
        "read_only": True,
        "device": device,
        "model": inventory.get("model"),
        "serial": inventory.get("serial"),
        "available": True,
        "tool": "smartctl",
        "exit_code": exit_code,
        "passed": smart_status.get("passed"),
        "temperature_c": _temperature_c(temperature.get("current", nvme.get("temperature"))),
        "power_on_hours": _as_optional_int(power_on.get("hours", nvme.get("power_on_hours"))),
        "power_cycles": _as_optional_int(payload.get("power_cycle_count", nvme.get("power_cycles"))),
        "percentage_used": _as_optional_int(nvme.get("percentage_used")),
        "available_spare_percent": _as_optional_int(nvme.get("available_spare")),
        "unsafe_shutdowns": _as_optional_int(nvme.get("unsafe_shutdowns")),
        "media_errors": _as_optional_int(nvme.get("media_errors")),
        "warnings": [str(item.get("string")) for item in messages if isinstance(item, dict) and item.get("string")],
    }


def _nvme_summary(
    device: str,
    inventory: dict[str, Any],
    payload: dict[str, Any],
    exit_code: int,
) -> dict[str, Any]:
    critical_warning = _as_optional_int(payload.get("critical_warning"))
    return {
        "read_only": True,
        "device": device,
        "model": inventory.get("model"),
        "serial": inventory.get("serial"),
        "available": True,
        "tool": "nvme",
        "exit_code": exit_code,
        "passed": critical_warning == 0 if critical_warning is not None else None,
        "critical_warning": critical_warning,
        "temperature_c": _temperature_c(payload.get("temperature")),
        "power_on_hours": _as_optional_int(payload.get("power_on_hours")),
        "power_cycles": _as_optional_int(payload.get("power_cycles")),
        "percentage_used": _as_optional_int(payload.get("percentage_used")),
        "available_spare_percent": _as_optional_int(payload.get("available_spare")),
        "unsafe_shutdowns": _as_optional_int(payload.get("unsafe_shutdowns")),
        "media_errors": _as_optional_int(payload.get("media_errors")),
    }


def _run_json(command: list[str]) -> dict[str, Any]:
    completed = _run_command(command, check=True)
    payload = _load_json(completed.stdout)
    if payload is None:
        raise SsdCliError(f"{command[0]} returned invalid JSON")
    return payload


def _run_command(command: list[str], *, check: bool) -> subprocess.CompletedProcess[str]:
    executable = shutil.which(command[0])
    if not executable:
        raise SsdCliError(f"Required CLI is not installed: {command[0]}")
    safe_command = [executable, *command[1:]]
    try:
        completed = subprocess.run(
            safe_command,
            shell=False,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT_SECONDS,
            env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C.UTF-8"},
        )
    except subprocess.TimeoutExpired as exc:
        raise SsdCliError(f"CLI timed out after {DEFAULT_TIMEOUT_SECONDS} seconds") from exc
    completed.stdout = completed.stdout[:MAX_OUTPUT_CHARS]
    completed.stderr = completed.stderr[:MAX_OUTPUT_CHARS]
    if check and completed.returncode != 0:
        message = (completed.stderr or completed.stdout).strip()[-2000:]
        raise SsdCliError(message or f"{command[0]} failed with exit code {completed.returncode}")
    return completed


def _load_json(value: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _is_ssd(device: dict[str, Any]) -> bool:
    rota = device.get("rota")
    transport = str(device.get("tran") or "").lower()
    return rota in (0, False, "0") or transport == "nvme"


def _collect_paths(device: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    path = str(device.get("path") or "")
    if path:
        paths.add(path)
    for child in device.get("children") or []:
        if isinstance(child, dict):
            paths.update(_collect_paths(child))
    return paths


def _partition_summary(children: object) -> list[dict[str, Any]]:
    if not isinstance(children, list):
        return []
    output: list[dict[str, Any]] = []
    for child in children:
        if not isinstance(child, dict):
            continue
        output.append(
            {
                "path": child.get("path"),
                "type": child.get("type"),
                "size_bytes": _as_int(child.get("size")),
                "filesystem": child.get("fstype"),
                "mountpoints": [item for item in child.get("mountpoints") or [] if item],
            }
        )
        output.extend(_partition_summary(child.get("children")))
    return output


def _clean(value: object) -> str | None:
    clean = str(value or "").strip()
    return clean or None


def _as_int(value: object) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _as_optional_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        match = re.search(r"-?\d+", str(value))
        return int(match.group()) if match else None


def _temperature_c(value: object) -> float | None:
    temperature = _as_optional_int(value)
    if temperature is None:
        return None
    if temperature > 200:
        return round(temperature - 273.15, 1)
    return float(temperature)


def _result(request_id: object, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: object, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}
