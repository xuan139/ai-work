FROM python:3.12-slim-bookworm

ARG AI_WORK_VERSION=development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    AI_WORK_VERSION=${AI_WORK_VERSION}

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/ai-work

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY static ./static
COPY README.md LICENSE ./

RUN groupadd --gid 10001 aiwork \
    && useradd --uid 10001 --gid aiwork --create-home aiwork \
    && mkdir -p data storage mock_nas/inbox mock_nas/processed \
    && chown -R aiwork:aiwork data storage mock_nas

USER aiwork

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl --fail --silent http://127.0.0.1:8000/healthz >/dev/null || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
