<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 08: Custom Dockerfile

## What this shows

`adk deploy cloud_run` generates the Dockerfile for you. When the image needs
something that generated file cannot hold, write your own: a `Dockerfile`, a
small FastAPI app built with `get_fast_api_app`, and `gcloud run deploy
--source .`. You lose the one-command convenience and gain control of
everything in the image.

Take this path when you need one of these:

| Need | Why `adk deploy cloud_run` falls short |
|---|---|
| Node.js in the image, for stdio MCP servers started with `npx` | The generated image is Python only |
| System packages (ffmpeg, Tesseract, Chromium, fonts) | No place to add `apt-get install` |
| Several agents in one service | One service per agent folder |
| Your own FastAPI middleware (auth, rate limits) | No hook to add middleware to the generated app |

Otherwise stay with `../03_adk_deploy_cloud_run/`.

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)) and the gcloud CLI, logged in:

  ```bash
  gcloud auth login
  gcloud auth application-default login
  export GCP_PROJECT=your-project-id
  gcloud config set project "$GCP_PROJECT"
  ```

- A project with billing enabled and these APIs on:

  ```bash
  gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
    artifactregistry.googleapis.com aiplatform.googleapis.com --project="$GCP_PROJECT"
  ```

- IAM for your own account (Owners already have all of these):

  ```bash
  ME="user:you@example.com"
  PROJECT_NUM=$(gcloud projects describe "$GCP_PROJECT" --format="value(projectNumber)")
  for ROLE in roles/run.sourceDeveloper roles/serviceusage.serviceUsageConsumer; do
    gcloud projects add-iam-policy-binding "$GCP_PROJECT" --member="$ME" --role="$ROLE"
  done
  # Deploying a service means acting as its runtime service account.
  gcloud iam service-accounts add-iam-policy-binding \
    "${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
    --member="$ME" --role="roles/iam.serviceAccountUser"
  ```

- Service accounts: the service builds and runs as the default compute service account,
  `<PROJECT_NUMBER>-compute@developer.gserviceaccount.com`. It needs
  `roles/cloudbuild.builds.builder` for the build (run `../07_cloud_build_perms/` once)
  and `roles/aiplatform.user` to call Gemini at run time:

  ```bash
  gcloud projects add-iam-policy-binding "$GCP_PROJECT" \
    --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
    --role="roles/aiplatform.user"
  ```
- Docker, only to build and run the image locally (optional; Cloud Build builds it for
  the deploy).
- For the local run: credentials in a `.env` at the repository root (see SETUP.md), or
  exported in your shell.

## Run it

Run the same app locally (`main.py` is the one custom server this module keeps, because
the custom image is the point of the topic):

1. `cd Module_15_Deployment/08_custom_dockerfile`
2. `set -a; source ../../.env; set +a`
3. `uvicorn main:app --port 8080`
4. In a second terminal:

   ```bash
   curl http://localhost:8080/health
   curl http://localhost:8080/list-apps
   NO_AUTH=1 URL=http://localhost:8080 APP_NAME=greet_agent bash ../09_curl_deployed_agent/test_deployed.sh "Priya"
   ```

With Docker installed you can run the image Cloud Run will build:

```bash
docker build -t greet-agent-custom .
docker run --rm -p 8080:8080 --env-file ../../.env greet-agent-custom
```

To look at the agent in the dev UI instead: `cd agents && adk web`, then select
`greet_agent`.

Deploy (this creates a private Cloud Run service and an Artifact Registry image):

1. `cd Module_15_Deployment/08_custom_dockerfile`
2. `export GCP_PROJECT=your-project-id`
3. `bash deploy.sh`

The script deploys a private service that uses Agent Platform (formerly Vertex AI)
through the service's identity, so no API key goes into the image. It sets
`GOOGLE_CLOUD_LOCATION=global` because `gemini-3.5-flash` is served from the global
location, not from the Cloud Run region. Call the service with an identity token:

```bash
URL=$(gcloud run services describe greet-agent-custom --region=us-central1 --format="value(status.url)")
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$URL/list-apps"
```

`../09_curl_deployed_agent/` shows a full session and `/run_sse` call.

## What to look for

- `/list-apps` returns `["greet_agent"]`. Add another package under `agents/`
  and it appears in the list without any change to `main.py`.
- The Dockerfile copies `requirements.txt` before the code, so rebuilding
  after a code change reuses the dependency layer.
- The container runs as a non-root user.

## Files

```
08_custom_dockerfile/
    Dockerfile          Python 3.12 slim, Node.js, non-root user
    main.py             FastAPI app from get_fast_api_app(agents_dir="agents")
    requirements.txt    google-adk, fastapi, uvicorn, aiosqlite
    .dockerignore       keeps .env, .venv, .git and local databases out
    deploy.sh           gcloud run deploy --source .
    agents/
        greet_agent/    a normal ADK agent package
```

`main.py` serves every package under `agents/`. The agent code is the same as
in `adk run`; only the wrapper around it changes.

## Common errors

| Symptom | Cause |
|---|---|
| `container failed to listen on the port defined by PORT` | The command hardcodes a port. Use `${PORT}`, as the Dockerfile does |
| `/list-apps` is empty | An agent folder under `agents/` is missing `__init__.py` or `root_agent` |
| `404 NOT_FOUND` for the model | `GOOGLE_CLOUD_LOCATION` is the Cloud Run region instead of `global` |
| `403 Forbidden` from the service | The service is private. Send an identity token, or grant `roles/run.invoker` |
| Sessions disappear | SQLite lives on the instance disk. Set `SESSION_DB_URL` to a managed database |

## Clean up

```bash
gcloud run services delete greet-agent-custom --region=us-central1 --project="$GCP_PROJECT"
gcloud artifacts docker images delete \
  "us-central1-docker.pkg.dev/$GCP_PROJECT/cloud-run-source-deploy/greet-agent-custom" \
  --delete-tags --project="$GCP_PROJECT"
docker rmi greet-agent-custom   # if you built it locally
rm -f sessions.db               # created by a local uvicorn run
```
