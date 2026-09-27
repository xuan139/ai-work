from __future__ import annotations

import json
import subprocess
import unittest
from unittest.mock import patch

from app.ssd_mcp import SSD_MCP_TOOLS, handle_ssd_mcp_request


LSBLK_PAYLOAD = {
    "blockdevices": [
        {
            "name": "nvme0n1",
            "path": "/dev/nvme0n1",
            "type": "disk",
            "size": 1000000000,
            "model": "Fast SSD",
            "serial": "SSD123",
            "rota": False,
            "tran": "nvme",
            "fstype": None,
            "mountpoints": [None],
            "children": [
                {
                    "name": "nvme0n1p1",
                    "path": "/dev/nvme0n1p1",
                    "type": "part",
                    "size": 900000000,
                    "fstype": "ext4",
                    "mountpoints": ["/"],
                }
            ],
        },
        {
            "name": "sdb",
            "path": "/dev/sdb",
            "type": "disk",
            "size": 2000000000,
            "model": "Rotating Disk",
            "serial": "HDD123",
            "rota": True,
            "tran": "sata",
            "fstype": None,
            "mountpoints": [None],
        },
    ]
}


class SsdMcpTests(unittest.TestCase):
    def test_lists_only_read_only_tools(self) -> None:
        response = handle_ssd_mcp_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        assert response is not None
        tools = response["result"]["tools"]
        self.assertEqual([tool["name"] for tool in tools], [tool["name"] for tool in SSD_MCP_TOOLS])
        self.assertTrue(all(tool["annotations"]["readOnlyHint"] for tool in tools))
        self.assertTrue(all(not tool["annotations"]["destructiveHint"] for tool in tools))

    @patch("app.ssd_mcp._run_command")
    def test_lists_non_rotational_devices(self, run_command) -> None:
        run_command.return_value = subprocess.CompletedProcess(
            ["lsblk"], 0, json.dumps(LSBLK_PAYLOAD), ""
        )
        response = handle_ssd_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "ssd_list_devices", "arguments": {}},
            }
        )
        assert response is not None
        result = response["result"]["structuredContent"]
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["devices"][0]["path"], "/dev/nvme0n1")
        self.assertEqual(result["devices"][0]["partitions"][0]["mountpoints"], ["/"])

    @patch("app.ssd_mcp._run_command")
    def test_usage_is_limited_to_detected_ssd_paths(self, run_command) -> None:
        df_output = (
            "Filesystem Type 1B-blocks Used Available Use% Mounted on\n"
            "/dev/nvme0n1p1 ext4 900000000 400000000 500000000 45% /\n"
            "/dev/sdb1 ext4 2000000000 1000000000 1000000000 50% /archive\n"
        )
        run_command.side_effect = [
            subprocess.CompletedProcess(["lsblk"], 0, json.dumps(LSBLK_PAYLOAD), ""),
            subprocess.CompletedProcess(["df"], 0, df_output, ""),
        ]
        response = handle_ssd_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "ssd_get_usage", "arguments": {}},
            }
        )
        assert response is not None
        result = response["result"]["structuredContent"]
        self.assertEqual(result["filesystem_count"], 1)
        self.assertEqual(result["filesystems"][0]["source"], "/dev/nvme0n1p1")
        self.assertEqual(result["filesystems"][0]["used_percent"], 45)

    @patch("app.ssd_mcp._run_command")
    @patch("app.ssd_mcp._health_command", return_value=["smartctl", "-a", "-j", "/dev/nvme0n1"])
    @patch("app.ssd_mcp._ssd_inventory")
    def test_health_returns_bounded_smart_summary(self, inventory, _health_command, run_command) -> None:
        device = {
            "path": "/dev/nvme0n1",
            "model": "Fast SSD",
            "serial": "SSD123",
        }
        inventory.return_value = ([device], {"/dev/nvme0n1"})
        payload = {
            "smartctl": {"messages": []},
            "smart_status": {"passed": True},
            "temperature": {"current": 39},
            "power_on_time": {"hours": 1200},
            "power_cycle_count": 42,
            "nvme_smart_health_information_log": {
                "percentage_used": 3,
                "available_spare": 100,
                "unsafe_shutdowns": 2,
                "media_errors": 0,
            },
        }
        run_command.return_value = subprocess.CompletedProcess(
            ["smartctl"], 0, json.dumps(payload), ""
        )
        response = handle_ssd_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "ssd_get_health", "arguments": {"device": "/dev/nvme0n1"}},
            }
        )
        assert response is not None
        result = response["result"]["structuredContent"]
        self.assertTrue(result["passed"])
        self.assertEqual(result["temperature_c"], 39.0)
        self.assertEqual(result["percentage_used"], 3)
        self.assertEqual(result["media_errors"], 0)

    def test_health_rejects_arbitrary_device_or_command_text(self) -> None:
        response = handle_ssd_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "ssd_get_health", "arguments": {"device": "/dev/nvme0n1; reboot"}},
            }
        )
        assert response is not None
        self.assertIn("error", response)
        self.assertIn("whole SSD path", response["error"]["message"])


if __name__ == "__main__":
    unittest.main()
