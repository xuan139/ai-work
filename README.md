# AI Work Meeting Demo

FastAPI demo for authenticated NAS-style meeting audio intake, browser recording, file upload, file discovery, transcription status, searchable meeting history, document RAG, and LLM call auditing.

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

## NAS Intake

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

## NAS Upload And RAG

The NAS Upload page accepts audio, video, PDF, DOCX, text, and general files.

- Audio files are routed to the Whisper analysis flow and marked as needing a speech model before real transcripts can be produced.
- Video files are routed to the YOLO analysis flow and marked as needing YOLO weights or a video analysis service.
- PDF files are parsed with `pypdf`, split into RAG chunks, and stored in SQLite under `document_chunks`.
- DOCX files are parsed with `python-docx` when the dependency is installed, then split into the same RAG chunk format.
- PDF/DOCX assets with RAG chunks show a document LLM input panel for document Q&A.
- If no model is selected for document Q&A, the UI prompts for a model before sending.
