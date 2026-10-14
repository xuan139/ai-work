"""Synthetic HIS and FHIR R4-shaped read tools; never loads patient data or URLs."""

import copy
import json
import re
from datetime import date
from app.hospital_demo_profiles import PROFILES

SNAPSHOT = "2026-10-14T09:00:00+08:00"
RESOURCE_TYPES = ["Patient", "Encounter", "Observation", "MedicationRequest", "Appointment"]
NOTICE = "虛構教學資料；固定時間快照，非真實病歷，不供診斷、開藥或治療決策。"


def _fixtures():
    resources = []
    for n, name, department, value in [
        (1, "示範病患甲", "家庭醫學科", 36.7),
        (2, "示範病患乙", "一般內科", 37.1),
        (3, "示範病患丙", "家庭醫學科", 36.5),
    ]:
        patient = f"demo-p{n:03}"
        subject = {"reference": f"Patient/{patient}"}
        encounter = f"demo-e{n:03}"
        resources.extend([
            {"resourceType": "Patient", "id": patient, "active": True,
             "identifier": [{"system": "https://hospital.example.invalid/mrn", "value": f"DEMO-{n:03}"}],
             "name": [{"use": "official", "text": name}]},
            {"resourceType": "Encounter", "id": encounter, "status": "finished",
             "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "AMB"},
             "subject": subject, "type": [{"text": department}],
             "period": {"start": f"2026-10-13T0{n+5}:00:00+08:00", "end": f"2026-10-13T0{n+5}:30:00+08:00"}},
            {"resourceType": "Observation", "id": f"demo-o{n:03}", "status": "final",
             "code": {"coding": [{"system": "http://loinc.org", "code": "8310-5", "display": "Body temperature"}]},
             "subject": subject, "encounter": {"reference": f"Encounter/{encounter}"},
             "effectiveDateTime": "2026-10-13T09:00:00+08:00",
             "valueQuantity": {"value": value, "unit": "°C", "system": "http://unitsofmeasure.org", "code": "Cel"}},
            {"resourceType": "Observation", "id": f"demo-o{n+100:03}", "status": "final",
             "code": {"coding": [{"system": "http://loinc.org", "code": "718-7", "display": "Hemoglobin [Mass/volume] in Blood"}]},
             "subject": subject, "encounter": {"reference": f"Encounter/{encounter}"},
             "effectiveDateTime": "2026-10-13T09:00:00+08:00",
             "valueQuantity": {"value": 13.0 + n / 10, "unit": "g/dL", "system": "http://unitsofmeasure.org", "code": "g/dL"}},
            {"resourceType": "MedicationRequest", "id": f"demo-m{n:03}", "status": "completed",
             "intent": "order", "subject": subject, "encounter": {"reference": f"Encounter/{encounter}"},
             "medicationCodeableConcept": {"text": "DEMO-MED 教學占位藥品（非實際藥物）"},
             "authoredOn": "2026-10-13", "note": [{"text": "不提供劑量或治療建議"}]},
            {"resourceType": "Appointment", "id": f"demo-a{n:03}", "status": "booked",
             "start": f"2026-10-15T0{n+5}:00:00+08:00", "end": f"2026-10-15T0{n+5}:30:00+08:00",
             "description": f"{department} 示範回診",
             "participant": [{"actor": subject, "status": "accepted"}]},
        ])
    return resources


RESOURCES = _fixtures()


def _tool(name, description, properties, required=()):
    return {"name": name, "description": description + " Synthetic demo data only; no clinical advice.",
            "inputSchema": {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False},
            "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}}


PATIENT = {"type": "string", "pattern": "^demo-p[0-9]{3}$"}
PAGE = {"offset": {"type": "integer", "minimum": 0, "maximum": 1000},
        "limit": {"type": "integer", "minimum": 1, "maximum": 20}}
HOSPITAL_MCP_TOOLS = [
    _tool("his_search_patients", "Find HIS patients by demo name, ID or medical record number.",
          {"query": {"type": "string", "maxLength": 100}, **PAGE}),
    _tool("his_patient_overview", "Read one patient's encounters, observations, medication orders, appointments and authored teaching interview, admission history and dietary notes; preserve source IDs. Dietary notes are not medical advice.",
          {"patient_id": PATIENT}, ["patient_id"]),
    _tool("his_list_appointments", "List demo appointments, optionally filtered by exact date and patient.",
          {"patient_id": PATIENT, "date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"}, **PAGE}),
    _tool("fhir_search_resources", "Search a limited FHIR R4-shaped resource collection; return searchset Bundle and pagination metadata, not a full FHIR REST server.",
          {"resource_type": {"type": "string", "enum": RESOURCE_TYPES}, "patient_id": PATIENT, **PAGE}, ["resource_type"]),
    _tool("fhir_read_resource", "Read one allowlisted FHIR R4-shaped resource by ID.",
          {"resource_type": {"type": "string", "enum": RESOURCE_TYPES},
           "resource_id": {"type": "string", "pattern": "^demo-[peoma][0-9]{3}$"}}, ["resource_type", "resource_id"]),
]


def _belongs(resource, patient_id):
    ref = f"Patient/{patient_id}"
    return (resource["resourceType"] == "Patient" and resource["id"] == patient_id
            or resource.get("subject", {}).get("reference") == ref
            or any(p.get("actor", {}).get("reference") == ref for p in resource.get("participant", [])))


def call_hospital_tool(name, arguments):
    tool = next((t for t in HOSPITAL_MCP_TOOLS if t["name"] == name), None)
    if not tool or not isinstance(arguments, dict):
        raise ValueError("Unknown read-only tool or invalid arguments")
    schema = tool["inputSchema"]
    if set(arguments) - set(schema["properties"]) or set(schema["required"]) - set(arguments):
        raise ValueError("Unexpected or missing arguments")
    for key, value in arguments.items():
        rule = schema["properties"][key]
        if rule["type"] == "integer":
            if type(value) is not int or not rule["minimum"] <= value <= rule["maximum"]:
                raise ValueError(f"Invalid {key}")
        elif not isinstance(value, str) or len(value) > rule.get("maxLength", 100):
            raise ValueError(f"Invalid {key}")
        if "enum" in rule and value not in rule["enum"] or "pattern" in rule and not re.fullmatch(rule["pattern"], value):
            raise ValueError(f"Invalid {key}")
    patient = arguments.get("patient_id")
    if "date" in arguments:
        date.fromisoformat(arguments["date"])
    if patient and not any(r["resourceType"] == "Patient" and r["id"] == patient for r in RESOURCES):
        raise ValueError("Demo patient not found")
    rows = [r for r in RESOURCES if not patient or _belongs(r, patient)]
    if name == "his_search_patients":
        query = arguments.get("query", "").strip().casefold()
        rows = [r for r in rows if r["resourceType"] == "Patient" and
                query in (r["id"] + r["name"][0]["text"] + r["identifier"][0]["value"]).casefold()]
    elif name == "his_list_appointments":
        rows = [r for r in rows if r["resourceType"] == "Appointment" and
                (not arguments.get("date") or r["start"][:10] == arguments["date"])]
    elif name.startswith("fhir_"):
        rows = [r for r in rows if r["resourceType"] == arguments["resource_type"]]
    result = {"demo": True, "notice": NOTICE, "snapshot_at": SNAPSHOT,
              "source": "AI Work HIS/FHIR Demo", "fhir_version": "4.0.1", "conformance": "demo subset; not a validated FHIR server"}
    if name == "his_patient_overview":
        result["teaching_profile"] = PROFILES[patient]
    if name == "fhir_read_resource":
        row = next((r for r in rows if r["id"] == arguments["resource_id"]), None)
        if row is None:
            raise ValueError("Demo resource not found")
        result["resource"] = row
    else:
        offset, limit = arguments.get("offset", 0), arguments.get("limit", 10)
        page = rows[offset:offset + limit]
        result.update(total=len(rows), offset=offset, next_offset=offset+limit if offset+limit < len(rows) else None)
        if name == "fhir_search_resources":
            result["bundle"] = {"resourceType": "Bundle", "type": "searchset", "total": len(rows),
                                "entry": [{"resource": r, "search": {"mode": "match"}} for r in page]}
        else:
            result["records"] = page
    return copy.deepcopy(result)


def handle_hospital_mcp_request(payload):
    request_id, method = payload.get("id"), payload.get("method")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        result = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {"listChanged": False}},
                  "serverInfo": {"name": "Hospital HIS / FHIR Demo", "version": "1.0.0"}, "instructions": NOTICE}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": HOSPITAL_MCP_TOOLS}
    elif method == "tools/call":
        params = payload.get("params")
        try:
            if not isinstance(params, dict):
                raise ValueError("Invalid tool parameters")
            output = call_hospital_tool(params.get("name"), params.get("arguments", {}))
            result = {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=False)}], "structuredContent": output, "isError": False}
        except ValueError as exc:
            result = {"content": [{"type": "text", "text": str(exc)}], "isError": True}
    else:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Unsupported read-only method"}}
    return {"jsonrpc": "2.0", "id": request_id, "result": result}
