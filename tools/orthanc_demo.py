"""Server-only preparation/seeding. Never exposed as an MCP or web write tool."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import sys
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.radiology_mcp import SOURCE, STUDIES, orthanc_request, locate_study

DIRECTORY = ROOT / "storage" / "orthanc"


def prepare():
    DIRECTORY.mkdir(parents=True, exist_ok=True, mode=0o700)
    config_path = DIRECTORY / "config.json"
    if config_path.exists():
        raise SystemExit("Configuration already exists; keep existing credentials and run seed/verify instead.")
    env = ROOT / ".env"
    content = env.read_text() if env.exists() else ""
    names = {line.split("=", 1)[0].strip() for line in content.splitlines() if "=" in line}
    keys = {"ORTHANC_URL", "ORTHANC_USER", "ORTHANC_PASSWORD", "RADIOLOGY_MCP_KEY"}
    if names & keys:
        raise SystemExit("Orthanc environment keys already exist; inspect configuration without overwriting.")
    username, password = "aiwork-demo", secrets.token_urlsafe(32)
    config = {"Name": "AI Work Orthanc Teaching Archive", "HttpPort": 8043,
              "HttpBindAddresses": ["127.0.0.1"], "RemoteAccessAllowed": False,
              "AuthenticationEnabled": True, "RegisteredUsers": {username: password},
              "StorageDirectory": str(DIRECTORY / "dicom"), "IndexDirectory": str(DIRECTORY / "index"),
              "DicomServerEnabled": False, "OrthancExplorerEnabled": False, "WebDavEnabled": False,
              "Plugins": [], "LuaScripts": [], "RestApiWriteToFileSystemEnabled": False,
              "ExecuteLuaEnabled": False, "HttpThreadsCount": 4, "MaximumStorageSize": 256,
              "MaximumStorageMode": "Reject"}
    backup = ROOT / "backups" / ("orthanc-prepare-" + time.strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True, mode=0o700)
    if env.exists():
        shutil.copy2(env, backup / "env.backup")
        os.chmod(backup / "env.backup", 0o600)
    for folder in ("dicom", "index", "bin"):
        (DIRECTORY / folder).mkdir(exist_ok=True, mode=0o700)
    with config_path.open("x") as stream:
        os.chmod(config_path, 0o600)
        json.dump(config, stream, indent=2)
    values = {"ORTHANC_URL": "http://127.0.0.1:8043", "ORTHANC_USER": username,
              "ORTHANC_PASSWORD": password, "RADIOLOGY_MCP_KEY": secrets.token_urlsafe(32)}
    staged = env.with_name(".env.orthanc-staged")
    with staged.open("x") as stream:
        os.chmod(staged, 0o600)
        stream.write(content.rstrip() + "\n" + "\n".join(k + "=" + v for k, v in values.items()) + "\n")
    os.replace(staged, env)
    print("Prepared loopback-only configuration. Environment backup:", backup)


def seed():
    from app.main import load_project_env
    load_project_env(ROOT / ".env")
    request = Request(SOURCE["image_url"], headers={"User-Agent": "AIWorkTeachingDemo/1.0"})
    with urlopen(request, timeout=60) as response:
        content = response.read(2 * 1024 * 1024 + 1)
    if hashlib.sha1(content).hexdigest() != SOURCE["sha1"]:
        raise SystemExit("Public source image changed; review licensing and pixels before import.")
    # Preserve the public JPEG as Secondary Capture, never claim original DX acquisition.
    for n, study in enumerate(STUDIES, start=1):
        existing = orthanc_request("/tools/find", {"Level": "Instance", "Query": {"SOPInstanceUID": study["instance_uid"]}})
        if not existing:
            orthanc_request("/tools/create-dicom", {"Force": True,
                "Tags": {"PatientID": study["patient_id"], "PatientName": f"AIWORK^DEMO{n:03}",
                         "PatientIdentityRemoved": "YES", "DeidentificationMethod": "Public CC0 JPEG; fictional demo metadata",
                         "InstitutionName": "AIWORK-TEACHING-ONLY", "StudyInstanceUID": study["study_uid"],
                         "SeriesInstanceUID": study["series_uid"], "SOPInstanceUID": study["instance_uid"],
                         "SOPClassUID": "1.2.840.10008.5.1.4.1.1.7", "Modality": "OT",
                         "StudyDescription": "DEMO chest radiograph - reused public image", "SeriesDescription": "CC0 teaching secondary capture",
                         "AccessionNumber": study["accession"], "StudyDate": "20261014", "SeriesNumber": "1", "InstanceNumber": "1"},
                "Content": "data:image/jpeg;base64," + base64.b64encode(content).decode()})
        locate_study(study["id"])
        print("Verified", study["id"])


def activate():
    from app.main import load_project_env
    from app.db import init_db, list_mcp_servers, update_mcp_server, update_mcp_server_sync
    from app.mcp_runtime import sync_streamable_http_tools
    load_project_env(ROOT / ".env")
    for study in STUDIES:
        locate_study(study["id"])
    init_db()
    server = next(s for s in list_mcp_servers() if s["slug"] == "orthanc-radiology")
    synced = sync_streamable_http_tools(server)
    assert len(synced["tools"]) == 6
    update_mcp_server_sync(server["id"], status="connected", protocol_version=synced["protocol_version"],
                           tools_json=json.dumps(synced["tools"]), tool_count=len(synced["tools"]), last_error=None)
    update_mcp_server(server["id"], {**server, "is_enabled": True})
    print("Orthanc Radiology MCP enabled with six read-only tools")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "seed", "activate"])
    globals()[parser.parse_args().action]()
