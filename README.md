# AI Work Meeting Demo

FastAPI demo for authenticated meeting recording, NAS-style file discovery, transcription status, and searchable meeting history.

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
