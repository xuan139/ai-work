"""Allowlisted teaching studies backed by a real, loopback-only Orthanc."""

import base64
import copy
import json
import os
import re
import uuid
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from app.hospital_mcp import RESOURCES

NOTICE = "虛構病患與教學報告；公開 CC0 影像重用於各示範檢查，不代表病患的實際影像，不供臨床診斷。"
SOURCE = {
    "title": "Normal posteroanterior (PA) chest radiograph (X-ray)",
    "author": "Mikael Häggström", "license": "CC0 1.0",
    "url": "https://commons.wikimedia.org/wiki/File:Normal_posteroanterior_(PA)_chest_radiograph_(X-ray).jpg",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/a1/Normal_posteroanterior_%28PA%29_chest_radiograph_%28X-ray%29.jpg",
    "sha1": "3124c4cf4c55eb3d2defa9b909f08f94e941ec43",
}


def dicom_uid(value):
    return "2.25." + str(uuid.uuid5(uuid.NAMESPACE_URL, "aiwork:radiology-demo:" + value).int)


STUDIES = [
    {"id": f"demo-xr{n:03}", "patient_id": f"demo-p{n:03}", "date": "2026-10-14",
     "accession": f"DEMO-XR-{n:03}", "description": "胸部 X 光教學影像 / Chest radiograph teaching image",
     "study_uid": dicom_uid(f"study-{n}"), "series_uid": dicom_uid(f"series-{n}"),
     "instance_uid": dicom_uid(f"instance-{n}"), "report_status": "pending" if n == 3 else "final"}
    for n in range(1, 4)
]
PATIENTS = [{"id": r["id"], "name": r["name"][0]["text"], "mrn": r["identifier"][0]["value"]}
            for r in RESOURCES if r["resourceType"] == "Patient"]


class OrthancError(RuntimeError):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def orthanc_request(path, payload=None, *, image=False):
    base = os.getenv("ORTHANC_URL", "http://127.0.0.1:8043").rstrip("/")
    parsed = urlparse(base)
    if (parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.username
            or parsed.password or parsed.path or parsed.query or parsed.fragment):
        raise OrthancError("ORTHANC_URL must be a loopback HTTP origin")
    username, password = os.getenv("ORTHANC_USER", ""), os.getenv("ORTHANC_PASSWORD", "")
    if not username or not password:
        raise OrthancError("需要設定 Orthanc 本機服務與帳密")
    # No caller-controlled paths, redirects or proxy environment are used.
    request = Request(base + path, data=json.dumps(payload).encode() if payload is not None else None,
                      headers={"Authorization": "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode(),
                               "Content-Type": "application/json", "Accept": "image/png" if image else "application/json"})
    try:
        with build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=15) as response:
            limit = 12 * 1024 * 1024 if image else 512 * 1024
            raw = response.read(limit + 1)
            if len(raw) > limit:
                raise OrthancError("Orthanc response exceeds the demo limit")
            if image:
                if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
                    raise OrthancError("Orthanc did not return a PNG preview")
                return raw
            return json.loads(raw)
    except HTTPError as exc:
        raise OrthancError(f"Orthanc request failed (HTTP {exc.code})") from None
    except (URLError, TimeoutError, OSError, ValueError):
        raise OrthancError("無法讀取 Orthanc，請檢查服務與教學影像匯入狀態") from None


def study_definition(study_id):
    study = next((s for s in STUDIES if s["id"] == study_id), None)
    if not study:
        raise ValueError("Unknown teaching study")
    return copy.deepcopy(study)


def locate_study(study_id):
    study = study_definition(study_id)
    records = orthanc_request("/tools/find", {"Level": "Instance", "Expand": True, "Limit": 2,
        "Query": {"PatientID": study["patient_id"], "StudyInstanceUID": study["study_uid"],
                  "SOPInstanceUID": study["instance_uid"]}})
    if not isinstance(records, list) or len(records) != 1:
        raise OrthancError("找不到唯一的 Orthanc 教學影像，請先完成匯入")
    instance = records[0].get("ID", "")
    if not re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{8}){4}", instance):
        raise OrthancError("Invalid Orthanc instance identifier")
    tags = orthanc_request(f"/instances/{instance}/simplified-tags")
    expected = {"PatientID": study["patient_id"], "StudyInstanceUID": study["study_uid"],
                "SOPInstanceUID": study["instance_uid"], "InstitutionName": "AIWORK-TEACHING-ONLY",
                "StudyDate": study["date"].replace("-", ""), "AccessionNumber": study["accession"],
                "SeriesInstanceUID": study["series_uid"], "SOPClassUID": "1.2.840.10008.5.1.4.1.1.7"}
    if any(tags.get(key) != value for key, value in expected.items()):
        raise OrthancError("影像不屬於允許的教學資料範圍")
    return {**study, "orthanc_instance_id": instance, "dicom_class": "Secondary Capture",
            "source": "Orthanc", "image_source": SOURCE, "notice": NOTICE}


def preview(study_id):
    study = locate_study(study_id)
    return orthanc_request(f"/instances/{study['orthanc_instance_id']}/preview", image=True)


def _tool(name, description, properties, required=()):
    return {"name": name, "description": description + " Teaching data only; never diagnose images.",
            "inputSchema": {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False},
            "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}}


PATIENT_ARG = {"type": "string", "enum": [p["id"] for p in PATIENTS]}
STUDY_ARG = {"type": "string", "enum": [s["id"] for s in STUDIES]}
RADIOLOGY_TOOLS = [
    _tool("radiology_search_patients", "List the fictional HIS patients available to this radiology demo.", {}),
    _tool("radiology_search_studies", "List allowlisted study metadata from Orthanc for a demo patient.", {"patient_id": PATIENT_ARG}, ["patient_id"]),
    _tool("radiology_get_study", "Read one Orthanc teaching study and source identifiers.", {"study_id": STUDY_ARG}, ["study_id"]),
    _tool("radiology_get_report", "Read the authored teaching report, not a clinician's report or image interpretation.", {"study_id": STUDY_ARG}, ["study_id"]),
    _tool("radiology_patient_timeline", "Read a patient's teaching study timeline, preserving dates and report status.", {"patient_id": PATIENT_ARG}, ["patient_id"]),
    _tool("radiology_open_viewer", "Return a same-origin, login-protected image viewer link.", {"study_id": STUDY_ARG}, ["study_id"]),
]


def call_radiology_tool(name, arguments):
    tool = next((t for t in RADIOLOGY_TOOLS if t["name"] == name), None)
    if not tool or not isinstance(arguments, dict):
        raise ValueError("Unknown read-only tool or arguments")
    schema = tool["inputSchema"]
    if set(arguments) != set(schema["required"]):
        raise ValueError("Unexpected or missing arguments")
    for key, value in arguments.items():
        if not isinstance(value, str) or value not in schema["properties"][key]["enum"]:
            raise ValueError("Invalid teaching resource identifier")
    result = {"demo": True, "notice": NOTICE}
    if name == "radiology_search_patients":
        return {**result, "patients": copy.deepcopy(PATIENTS), "source": "Hospital HIS Demo"}
    if name in {"radiology_search_studies", "radiology_patient_timeline"}:
        studies = [locate_study(s["id"]) for s in STUDIES if s["patient_id"] == arguments["patient_id"]]
        return {**result, "studies": sorted(studies, key=lambda s: (s["date"], s["id"]), reverse=True)}
    study = locate_study(arguments["study_id"])
    if name == "radiology_get_study":
        return {**result, "study": study}
    if name == "radiology_open_viewer":
        return {**result, "url": "/radiology-demo?study=" + study["id"],
                "preview_url": "/api/radiology-demo/studies/" + study["id"] + "/image",
                "study_id": study["id"], "image_source": SOURCE}
    report = {"id": "report-" + study["id"], "study_id": study["id"], "status": study["report_status"],
              "source": "AI Work authored teaching report", "version": 1, "date": study["date"],
              "text": None if study["report_status"] == "pending" else
                  "教學報告：本筆胸部影像用於展示影像歸檔、查詢與報告摘要流程。影像來自公開 CC0 素材，"
                  "以 Secondary Capture DICOM 匯入 Orthanc，並非此虛構病患實際接受攝影所得。"
                  "本報告未包含臨床判讀、診斷或治療建議；不可從本資料推論病患健康狀況。"}
    return {**result, "report": report}


def handle_radiology_mcp(payload):
    method, request_id = payload.get("method"), payload.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        result = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}},
                  "serverInfo": {"name": "Orthanc Radiology Demo", "version": "1.0.0"}, "instructions": NOTICE}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": RADIOLOGY_TOOLS}
    elif method == "tools/call":
        try:
            params = payload.get("params")
            if not isinstance(params, dict):
                raise ValueError("Invalid parameters")
            output = call_radiology_tool(params.get("name"), params.get("arguments", {}))
            result = {"structuredContent": output, "content": [{"type": "text", "text": json.dumps(output, ensure_ascii=False)}], "isError": False}
        except (ValueError, OrthancError) as exc:
            result = {"content": [{"type": "text", "text": str(exc)}], "isError": True}
    else:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Unsupported read-only method"}}
    return {"jsonrpc": "2.0", "id": request_id, "result": result}
