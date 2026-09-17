# AI Work Meeting Demo

FastAPI demo for authenticated NAS-style meeting audio intake, browser recording, file upload, file discovery, transcription status, searchable meeting history, document RAG, and LLM call auditing.

Administrators can manage Portal accounts from the Account Management view: create users, assign roles, enable or disable access, reset passwords, and safely remove unused standard accounts. Access or password changes revoke existing sessions.

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

## Long Audio Uploads And Chinese Script

- Web uploads are streamed to storage in 1 MB chunks. The application default limit is 2 GB and can be changed with `AI_WORK_MAX_UPLOAD_BYTES`.
- Production reverse proxies must allow the same body size. An Nginx include example is available at `deploy/nginx-ai-work-upload.conf`.
- The NAS upload page shows actual browser upload progress for large recordings and does not impose a client-side timeout.
- `whisper.cpp` processing defaults to a four-hour timeout and ffmpeg conversion defaults to one hour. Override them with `ASR_PROCESS_TIMEOUT_SECONDS` and `ASR_FFMPEG_TIMEOUT_SECONDS`.
- ASR output is normalized to Traditional Chinese with OpenCC before it is audited, stored, indexed, translated, or pushed to LINE. Set `ASR_CHINESE_SCRIPT=simplified` for Simplified Chinese or `ASR_CHINESE_SCRIPT=none` to preserve the engine output.
- Audio and video jobs are dispatched to an application background worker queue after upload. `MEDIA_WORKER_COUNT` defaults to `1` so local models do not compete for RAM or GPU memory.
- Media larger than 100 MB is automatically segmented. Audio longer than 30 minutes and video longer than 10 minutes are also segmented even when compressed below that size. Override these limits with `MEDIA_SPLIT_THRESHOLD_BYTES`, `AUDIO_SPLIT_THRESHOLD_SECONDS`, and `VIDEO_SPLIT_THRESHOLD_SECONDS`.
- Audio segments default to 10 minutes and are normalized to 16 kHz mono WAV before ASR; video segments default to 5 minutes. Configure them with `AUDIO_SEGMENT_SECONDS` and `VIDEO_SEGMENT_SECONDS`.
- Segment progress is stored in the NAS asset status. Temporary segment files are removed after the worker merges transcripts or video detections; the original NAS file remains unchanged.

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

The NAS Upload page accepts audio, video, image, PDF, DOCX, text, and general files.

- The upload page shows NAS-oriented operating context: volume name, SMB / NFS / WebDAV entry points, snapshot retention, and access control source.
- Each NAS asset detail page includes a processing timeline that lists the service, parser, or model used at every step.
- Audio uploads let the user choose a local NAS ASR model or a cloud ASR API before intake.
- Browser recordings and audio uploads share the same ASR selector and processing path.
- Local ASR options include `whisper.cpp`, `faster-whisper`, `SenseVoiceSmall`, and `Paraformer-zh`; they run only when the corresponding runtime and model files are installed on the NAS host.
- `whisper.cpp` uses CPU by default so it can coexist with the local GPU LLM. Set `WHISPER_CPP_USE_GPU=1` to enable its GPU backend. Python ASR runtimes can be installed with `pip install -r requirements-asr.txt`.
- Cloud ASR options include OpenAI Transcribe, Deepgram Nova-3, and AssemblyAI Universal. The API key is used only for the current upload and is not written to SQLite.
- Every ASR success or failure is written to the model call audit table with caller, model, input file descriptor, output, status, and timestamp.
- Successful ASR output is split into `audio_transcript` chunks in `document_chunks`, so audio meeting content can be queried through the same RAG panel as PDF/DOCX.
- The NAS Model Management panel shows local ASR installation state, local file size, download progress, runtime readiness, and model file path.
- `whisper.cpp` model downloads are explicit user actions from the NAS panel. Cancel leaves the partial file in place; retry resumes the same model file.
- The transcription runtime checks expected model size before using a local `whisper.cpp` model, so partial downloads are never treated as installed.
- Video files are routed to the YOLO analysis flow and marked as needing YOLO weights or a video analysis service.
- YOLO inference defaults to CPU even when its deployment environment is recreated. Set `YOLO_DEVICE=cuda:0` (or another Ultralytics device value) to request an accelerator; failed non-CPU inference automatically retries once on CPU and records the requested and effective devices in each video RAG chunk.
- PDF files render every page image with `PyMuPDF`; files with a text layer are parsed with `pypdf`, while image-only PDFs fall back to `PaddleOCR` when it is installed.
- PDF RAG chunks store page number, chunk type, and page preview image path, so document Q&A can show source page previews with the model answer.
- JPG, PNG, WebP, TIFF, and BMP images are processed by PaddleOCR into `image_ocr` chunks, embedded for hybrid retrieval, and shown as source previews in image RAG answers.
- DOCX files are parsed with `python-docx` when the dependency is installed, then split into the same RAG chunk format.
- PDF/DOCX assets with RAG chunks show a document LLM input panel for document Q&A through the selected LLM provider.
- If no model is selected for document Q&A, the UI prompts for a model before sending.
- For scanned or image-based PDFs, install the optional OCR engine with `pip install -r requirements-ocr.txt`; without it the asset status shows that an OCR engine is required. On macOS arm64, use Python 3.12 for PaddlePaddle support.
