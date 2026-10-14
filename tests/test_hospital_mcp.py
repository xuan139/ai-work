import copy
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from app import db, main
from app.auth import current_user
from app.hospital_mcp import RESOURCES, HOSPITAL_MCP_TOOLS, call_hospital_tool, handle_hospital_mcp_request


class HospitalTests(unittest.TestCase):
    def test_discovery(self):
        self.assertEqual(len(HOSPITAL_MCP_TOOLS), 5)
        self.assertTrue(all(t["annotations"]["readOnlyHint"] for t in HOSPITAL_MCP_TOOLS))
        for method in ("initialize", "ping", "tools/list"):
            self.assertIn("result", handle_hospital_mcp_request({"id": 1, "method": method}))
        self.assertIsNone(handle_hospital_mcp_request({"method": "notifications/initialized"}))

    def test_search_and_patient_isolation(self):
        result = call_hospital_tool("his_search_patients", {"query": "DEMO-002"})
        self.assertEqual(result["records"][0]["id"], "demo-p002")
        overview = call_hospital_tool("his_patient_overview", {"patient_id": "demo-p002"})
        self.assertEqual(len(overview["records"]), 6)
        self.assertTrue(all(r.get("subject", {"reference": "Patient/demo-p002"})["reference"] == "Patient/demo-p002" for r in overview["records"]))
        self.assertTrue(overview["demo"])

    def test_fhir_his_agree_and_references_resolve(self):
        his = call_hospital_tool("his_patient_overview", {"patient_id": "demo-p001"})
        for resource in his["records"]:
            read = call_hospital_tool("fhir_read_resource", {"resource_type": resource["resourceType"], "resource_id": resource["id"]})
            self.assertEqual(resource, read["resource"])
        refs = {r["resourceType"] + "/" + r["id"] for r in RESOURCES}
        for resource in RESOURCES:
            for field in ("subject", "encounter"):
                if field in resource:
                    self.assertIn(resource[field]["reference"], refs)
            for p in resource.get("participant", []):
                self.assertIn(p["actor"]["reference"], refs)

    def test_pagination_and_empty_results(self):
        a = call_hospital_tool("fhir_search_resources", {"resource_type": "Patient", "limit": 2})
        b = call_hospital_tool("fhir_search_resources", {"resource_type": "Patient", "offset": a["next_offset"], "limit": 2})
        self.assertEqual(a["bundle"]["type"], "searchset")
        self.assertEqual(a["total"], 3)
        self.assertEqual(len(b["bundle"]["entry"]), 1)
        self.assertIsNone(b["next_offset"])
        self.assertEqual(call_hospital_tool("his_search_patients", {"query": "nonexistent"})["total"], 0)
        self.assertEqual(call_hospital_tool("his_list_appointments", {"date": "2026-10-15", "patient_id": "demo-p001"})["total"], 1)

    def test_invalid_arguments_and_writes(self):
        cases = [("his_search_patients", {"limit": True}), ("his_search_patients", {"limit": 100}),
                 ("his_search_patients", {"query": None}), ("his_search_patients", {"url": "http://localhost"}),
                 ("his_patient_overview", {}), ("his_patient_overview", {"patient_id": "demo-p999"}),
                 ("fhir_read_resource", {"resource_type": "Patient", "resource_id": "../../etc/passwd"}),
                 ("fhir_search_resources", {"resource_type": "Binary"}), ("fhir_create", {}),
                 ("fhir_read_resource", {"resource_type": "Patient", "resource_id": "demo-p999"})]
        for name, args in cases:
            with self.subTest(name=name, args=args):
                result = handle_hospital_mcp_request({"id": 1, "method": "tools/call", "params": {"name": name, "arguments": args}})
                self.assertTrue(result["result"]["isError"])
        self.assertIn("error", handle_hospital_mcp_request({"id": 1, "method": "resources/write"}))

    def test_output_cannot_mutate_fixture(self):
        before = copy.deepcopy(RESOURCES)
        result = call_hospital_tool("his_search_patients", {})
        result["records"][0]["name"][0]["text"] = "changed"
        self.assertEqual(before, RESOURCES)

    def test_endpoint_auth_and_real_http_transport(self):
        client = TestClient(main.app)
        payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        try:
            with patch.dict(os.environ, {"HOSPITAL_DEMO_MCP_KEY": ""}):
                self.assertEqual(client.post("/mcp/hospital-demo", json=payload).status_code, 503)
            with patch.dict(os.environ, {"HOSPITAL_DEMO_MCP_KEY": "test-key"}):
                self.assertEqual(client.post("/mcp/hospital-demo", json=payload).status_code, 401)
                headers = {"Authorization": "Bearer test-key"}
                response = client.post("/mcp/hospital-demo", json=payload, headers=headers)
                self.assertEqual(len(response.json()["result"]["tools"]), 5)
                payload.update(method="tools/call", params={"name": "his_patient_overview", "arguments": {"patient_id": "demo-p001"}})
                self.assertEqual(client.post("/mcp/hospital-demo", json=payload, headers=headers).json()["result"]["structuredContent"]["total"], 6)
                self.assertEqual(client.delete("/mcp/hospital-demo", headers=headers).status_code, 405)
        finally:
            client.close()

    def test_registry_seed_is_idempotent_and_disabled(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(db, "DB_PATH", Path(directory) / "app.db"):
            db.init_db()
            db.seed_admin("unused-test-hash")
            db.seed_admin("unused-test-hash")
            rows = [s for s in db.list_mcp_servers() if s["slug"] == "hospital-demo"]
            self.assertEqual(len(rows), 1)
            self.assertFalse(rows[0]["is_enabled"])
            self.assertEqual(rows[0]["auth_env_var"], "HOSPITAL_DEMO_MCP_KEY")

    def test_demo_page_auth_tool_scope_and_audit(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(db, "DB_PATH", Path(directory) / "app.db"):
            db.init_db()
            db.seed_admin("unused-test-hash")
            admin = db.get_user_by_username("admin")
            server = next(s for s in db.list_mcp_servers() if s["slug"] == "hospital-demo")
            client = TestClient(main.app)
            try:
                self.assertEqual(client.get("/hospital-demo").status_code, 200)
                payload = {"name": "his_search_patients", "arguments": {}}
                self.assertEqual(client.post("/api/hospital-demo/tools/call", json=payload).status_code, 401)
                main.app.dependency_overrides[current_user] = lambda: admin
                self.assertEqual(client.post("/api/hospital-demo/tools/call", json=payload).status_code, 503)
                with patch.object(main, "available_mcp_servers", return_value=[server]), patch.object(main, "call_streamable_http_tool") as call:
                    call.return_value = {"structuredContent": call_hospital_tool("his_search_patients", {})}
                    response = client.post("/api/hospital-demo/tools/call", json=payload)
                    self.assertEqual(response.json()["result"]["structuredContent"]["total"], 3)
                    call.assert_called_once_with(server, "his_search_patients", {})
                    for name in ["delete_patient", [], None]:
                        self.assertEqual(client.post("/api/hospital-demo/tools/call", json={"name": name}).status_code, 400)
                    call.side_effect = ValueError("Rejected invalid patient")
                    self.assertEqual(client.post("/api/hospital-demo/tools/call", json=payload).status_code, 502)
                with db.connect() as conn:
                    rows = conn.execute("SELECT status, user_id FROM mcp_audit_logs ORDER BY id").fetchall()
                self.assertEqual([r["status"] for r in rows], ["completed", "failed"])
                self.assertTrue(all(r["user_id"] == admin["id"] for r in rows))
            finally:
                main.app.dependency_overrides.clear()
                client.close()


if __name__ == "__main__":
    unittest.main()
