# AI Work Meeting Demo

FastAPI demo for authenticated NAS-style meeting audio intake, browser recording, file discovery, transcription status, searchable meeting history, and LLM call auditing.

## Run

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

Default login:

- username: `admin`
- password: `admin123`

## Simulated NAS

Drop an audio file into:

```text
mock_nas/inbox/
```

The app detects it, shows a browser notification popup, copies the audio into `storage/recordings/`, moves the original into `mock_nas/processed/`, and starts the transcription adapter.

NAS demo behaviors shown in the UI:

- `mock_nas/inbox/` acts as the shared SMB / NFS-style drop zone.
- New audio files are detected by a backend watcher and surfaced as popup notifications.
- Source voice files are archived under `storage/recordings/`.
- Original NAS files are moved into `mock_nas/processed/` after intake.
- Meeting metadata, source, timestamps, status, and transcript text are indexed in SQLite.
- Authenticated users query NAS meeting assets through the meeting database page.
- AI Work can audit model calls against the NAS meeting knowledge workflow.
