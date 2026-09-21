# AI Work n8n deployment

This deployment runs n8n on `127.0.0.1:5678` and publishes it at
`https://goldsys.io/n8n/`. Nginx delegates access control to the AI Work
`/auth/n8n` endpoint, which only accepts authenticated administrators.

Create `.env` from `.env.example` with a persistent encryption key and a
separate webhook token. Set the same `N8N_WEBHOOK_TOKEN` in the AI Work
`.env`, then start the pinned image:

```bash
docker compose pull
docker compose up -d
```

Inject the dedicated token into a server-only copy, then import and publish the
automatic NAS workflow after the service is ready:

```bash
token=$(sed -n 's/^N8N_WEBHOOK_TOKEN=//p' .env)
sed "s/__AI_WORK_N8N_TOKEN__/$token/g" bootstrap/ai-work-nas-asset-completed.json > bootstrap/ai-work-nas-asset-completed.runtime.json
unset token
docker compose exec -T n8n n8n import:workflow --input=/bootstrap/ai-work-nas-asset-completed.runtime.json
docker compose exec -T n8n n8n publish:workflow --id=1da52e2e-2897-45cd-978c-a11f86cb7bdd
```

When an audio or PDF asset finishes processing, AI Work posts the result to
the n8n production webhook. The workflow records the execution and calls the
protected AI Work callback, which pushes a preview to the configured approved
company LINE group.

The runtime workflow copy contains the callback token and must not be committed.
n8n remains restricted to AI Work administrators, and workflow nodes cannot read
other container environment variables.
