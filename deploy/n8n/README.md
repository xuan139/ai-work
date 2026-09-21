# AI Work n8n deployment

This deployment runs n8n on `127.0.0.1:5678` and publishes it at
`https://goldsys.io/n8n/`. Nginx delegates access control to the AI Work
`/auth/n8n` endpoint, which only accepts authenticated administrators.

Create `.env` from `.env.example` with a persistent random encryption key,
then start the pinned image:

```bash
docker compose pull
docker compose up -d
```

Import the bundled manual test workflow after the service is ready:

```bash
docker compose exec -T n8n n8n import:workflow --input=/bootstrap/ai-work-nas-test.json
```
