import asyncio
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient
from app import db, main, radiology_demo as demo, radiology_mcp as mcp
from app.auth import current_user

INSTANCE = "12345678-12345678-12345678-12345678-12345678"


def orthanc_fixture(path, payload=None, **kwargs):
    if path == "/tools/find":
        return [{"ID": INSTANCE}]
    if path.endswith("/simplified-tags"):
        s = mcp.STUDIES[0]
        return {"PatientID": s["patient_id"], "StudyInstanceUID": s["study_uid"],
                "SOPInstanceUID": s["instance_uid"], "InstitutionName": "AIWORK-TEACHING-ONLY",
                "StudyDate": "20261014", "AccessionNumber": s["accession"],
                "SeriesInstanceUID": s["series_uid"], "SOPClassUID": "1.2.840.10008.5.1.4.1.1.7"}
    if path.endswith("/preview"):
        return b"\x89PNG\r\n\x1a\nfixture"
    raise AssertionError(path)


def located(study_id):
    return {**mcp.study_definition(study_id), "orthanc_instance_id": INSTANCE,
            "dicom_class": "Secondary Capture", "image_source": mcp.SOURCE}


class RadiologyTests(unittest.TestCase):
    def test_tools_and_strict_scope(self):
        self.assertEqual(len(mcp.RADIOLOGY_TOOLS), 6)
        self.assertTrue(all(t["annotations"]["readOnlyHint"] for t in mcp.RADIOLOGY_TOOLS))
        with patch.object(mcp, "orthanc_request") as request:
            for name, args in [("delete_study", {}), ("radiology_get_study", {"study_id": "../../system"}),
                               ("radiology_get_study", {"study_id": []}), ("radiology_get_study", {}),
                               ("radiology_search_patients", {"url": "http://169.254.169.254"}),
                               ("radiology_get_study", {"study_id": "demo-xr001", "write": True})]:
                with self.assertRaises(ValueError):
                    mcp.call_radiology_tool(name, args)
            request.assert_not_called()

    def test_orthanc_identity_and_missing_checks(self):
        with patch.object(mcp, "orthanc_request", side_effect=orthanc_fixture) as request:
            self.assertEqual(mcp.locate_study("demo-xr001")["orthanc_instance_id"], INSTANCE)
            self.assertEqual(request.call_args_list[0].args[1]["Query"]["PatientID"], "demo-p001")
            self.assertTrue(mcp.preview("demo-xr001").startswith(b"\x89PNG"))
        with patch.object(mcp, "orthanc_request", return_value=[]):
            with self.assertRaises(mcp.OrthancError):
                mcp.locate_study("demo-xr001")
        for mismatch in [{"PatientID": "real-patient"}, {"InstitutionName": "REAL-HOSPITAL"}]:
            tags = orthanc_fixture("/instances/test/simplified-tags") | mismatch
            with patch.object(mcp, "orthanc_request", side_effect=[[{"ID": INSTANCE}], tags]):
                with self.assertRaises(mcp.OrthancError):
                    mcp.locate_study("demo-xr001")

    def test_report_and_source_links(self):
        before = copy.deepcopy(mcp.STUDIES)
        with patch.object(mcp, "locate_study", side_effect=located):
            for tool in mcp.RADIOLOGY_TOOLS:
                args = {key: ("demo-p001" if key == "patient_id" else "demo-xr001") for key in tool["inputSchema"]["required"]}
                result = mcp.call_radiology_tool(tool["name"], args)
                self.assertTrue(result["demo"])
            pending = mcp.call_radiology_tool("radiology_get_report", {"study_id": "demo-xr003"})
            self.assertIsNone(pending["report"]["text"])
            viewer = mcp.call_radiology_tool("radiology_open_viewer", {"study_id": "demo-xr001"})
            self.assertEqual(viewer["preview_url"], "/api/radiology-demo/studies/demo-xr001/image")
        self.assertEqual(before, mcp.STUDIES)

    def test_transport_rejects_remote_origins_and_missing_credentials(self):
        for url in ["http://example.com", "http://127.0.0.1@evil.test", "http://127.0.0.1/path", "http://127.0.0.1?x=1"]:
            with patch.dict(os.environ, {"ORTHANC_URL": url}), patch.object(mcp, "build_opener") as opener:
                with self.assertRaises(mcp.OrthancError):
                    mcp.orthanc_request("/system")
                opener.assert_not_called()
        with patch.dict(os.environ, {"ORTHANC_URL": "http://127.0.0.1:8043", "ORTHANC_PASSWORD": ""}):
            with self.assertRaises(mcp.OrthancError):
                mcp.orthanc_request("/system")

    def test_rpc(self):
        result = mcp.handle_radiology_mcp({"id": 1, "method": "tools/call", "params": {"name": "delete"}})
        self.assertTrue(result["result"]["isError"])
        self.assertEqual(len(mcp.handle_radiology_mcp({"id": 1, "method": "tools/list"})["result"]["tools"]), 6)

    def test_summary_uses_mcp_evidence_and_rejects_pending(self):
        async def execute(name, args, user):
            with patch.object(mcp, "locate_study", side_effect=located):
                return {"tool": name, "arguments": args, "result": mcp.call_radiology_tool(name, args)}
        model = AsyncMock(return_value={"answer": "教學報告 [R1]，檢查 [S1]。", "call_id": 5})
        with patch.object(demo, "execute", side_effect=execute):
            result = asyncio.run(demo.summarize("demo-xr001", "摘要", {"id": 1}, "test-model", model))
            self.assertFalse(result["citation_warning"])
            self.assertEqual([s["id"] for s in result["sources"]], ["S1", "R1"])
            self.assertEqual(len(result["steps"]), 2)
            self.assertIn("report-demo-xr001", model.call_args.kwargs["prompt"])
            self.assertNotIn("base64", model.call_args.kwargs["prompt"])
            with self.assertRaises(HTTPException) as exc:
                asyncio.run(demo.summarize("demo-xr003", "摘要", {"id": 1}, "test-model", model))
            self.assertEqual(exc.exception.status_code, 409)
            self.assertEqual(model.await_count, 1)
            model.return_value = {"answer": "No citation", "call_id": 6}
            self.assertTrue(asyncio.run(demo.summarize("demo-xr001", "摘要", {"id": 1}, "test-model", model))["citation_warning"])

    def test_auth_disabled_audit_and_no_store(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(db, "DB_PATH", Path(directory) / "app.db"):
            db.init_db(); db.seed_admin("unused")
            user = db.get_user_by_username("admin")
            server = next(s for s in db.list_mcp_servers() if s["slug"] == "orthanc-radiology")
            self.assertFalse(server["is_enabled"])
            client = TestClient(main.app)
            try:
                for route in ["/api/radiology-demo/tools/call", "/api/radiology-demo/summary"]:
                    self.assertEqual(client.post(route, json={}).status_code, 401)
                self.assertEqual(client.get("/api/radiology-demo/studies/demo-xr001/image").status_code, 401)
                with patch.dict(os.environ, {"RADIOLOGY_MCP_KEY": "test-secret"}):
                    self.assertEqual(client.post("/mcp/radiology-demo", json={}).status_code, 401)
                    r = client.post("/mcp/radiology-demo", json={"method": "tools/list", "id": 1}, headers={"Authorization": "Bearer test-secret"})
                    self.assertEqual(r.status_code, 200)
                    self.assertEqual(r.headers["cache-control"], "no-store")
                main.app.dependency_overrides[current_user] = lambda: user
                payload = {"name": "radiology_search_patients", "arguments": {}}
                self.assertEqual(client.post("/api/radiology-demo/tools/call", json=payload).status_code, 503)
                with patch.object(demo, "connected_server", return_value=server), patch.object(demo, "call_streamable_http_tool") as call:
                    call.return_value = {"structuredContent": {"patients": mcp.PATIENTS}}
                    self.assertEqual(client.post("/api/radiology-demo/tools/call", json=payload).status_code, 200)
                    call.side_effect = ValueError("Service unavailable")
                    self.assertEqual(client.post("/api/radiology-demo/tools/call", json=payload).status_code, 502)
                    with patch.object(demo, "preview", return_value=b"\x89PNG\r\n\x1a\nfixture"):
                        response = client.get("/api/radiology-demo/studies/demo-xr001/image")
                        self.assertEqual(response.headers["cache-control"], "no-store")
                with db.connect() as connection:
                    rows = connection.execute("SELECT status,user_id FROM mcp_audit_logs ORDER BY id").fetchall()
                self.assertEqual([row["status"] for row in rows], ["completed", "failed", "completed"])
                self.assertTrue(all(row["user_id"] == user["id"] for row in rows))
            finally:
                main.app.dependency_overrides.clear(); client.close()


if __name__ == "__main__":
    unittest.main()
