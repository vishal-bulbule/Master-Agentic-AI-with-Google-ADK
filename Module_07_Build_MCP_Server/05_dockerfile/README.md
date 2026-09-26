<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 05: Dockerfile and Cloud Run Deploy

## What this shows

What it takes to ship the stateless Streamable HTTP server from
`../04_streamable_http_server/` as a container on Cloud Run.

| File | Purpose |
|---|---|
| `server.py` | Copy of `../04_streamable_http_server/server.py`, so this folder builds on its own |
| `requirements.txt` | `mcp`, `starlette`, `uvicorn` |
| `Dockerfile` | Python 3.12 slim, non-root user, `python server.py` on `$PORT` |
| `.dockerignore` | Keeps caches, virtual environments, and `.env` files out of the image |

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)), virtual environment active.
- Node.js with `npx`, for MCP Inspector.
- For the container steps: Docker (optional; `gcloud run deploy --source .`
  builds in Cloud Build without it).
- For the deploy: the `gcloud` CLI, authenticated (`gcloud auth login`), and a
  project with billing enabled and these APIs on:

  ```bash
  gcloud config set project YOUR_PROJECT_ID
  gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
  ```

  Your account needs permission to deploy Cloud Run services from source
  (for example Cloud Run Admin, Cloud Build Editor, Artifact Registry Admin,
  and Service Account User on the runtime service account).
- No model API keys: the server does not call a model.

## Run it

Locally without Docker, the same command the container runs:

1. `cd Module_07_Build_MCP_Server/05_dockerfile`
2. `python server.py`
3. In another terminal: `npx @modelcontextprotocol/inspector --cli http://localhost:8080/mcp --method tools/list`

With Docker, from the same folder:

```bash
docker build -t my-mcp-server .
docker run --rm -p 8080:8080 my-mcp-server
```

Deploy to Cloud Run (Cloud Build builds the image from this folder):

```bash
gcloud run deploy my-mcp-server \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated
```

`--no-allow-unauthenticated` makes Cloud Run reject any request without an
identity token from a principal that has `roles/run.invoker`. Only use
`--allow-unauthenticated` for a throwaway test service.

gcloud prints the service URL. The MCP endpoint is `<service URL>/mcp`:

```python
McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://my-mcp-server-xxxxxxxxxx.us-central1.run.app/mcp",
        headers={"Authorization": f"Bearer {id_token}"},  # when IAM auth is on
    ),
)
```

For a caller running on Google Cloud, fetch `id_token` for the service URL
with `google.oauth2.id_token.fetch_id_token`; locally,
`gcloud auth print-identity-token` works for a quick test.

## What to look for

- `server.py` reads `PORT` and binds `0.0.0.0`. Hardcoding a port or binding
  `127.0.0.1` works locally and fails health checks on Cloud Run.
- `stateless=True` in `server.py`. Without it, a client's second request can
  land on another instance that has never seen its session.

## Common errors

| Symptom | Cause and fix |
|---|---|
| Container fails to start on Cloud Run | Check the logs for an import error; `requirements.txt` must list everything `server.py` imports. |
| First request is slow | A cold start. Set `--min-instances 1` if latency matters more than the cost of an idle instance. |
| 403 from Cloud Run | IAM is on and the caller has no `roles/run.invoker`, or the identity token was minted for a different audience. |

## Clean up

```bash
gcloud run services delete my-mcp-server --region us-central1
docker rmi my-mcp-server   # if you built locally
```

`--source` deploys push the image to the `cloud-run-source-deploy` Artifact
Registry repository in the same region; delete the image there if you no
longer need it.
