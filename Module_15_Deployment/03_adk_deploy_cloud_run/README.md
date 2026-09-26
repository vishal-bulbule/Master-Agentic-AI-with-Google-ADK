<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 03 - `adk deploy cloud_run`

## What this shows

One command from an agent folder to a `https://*.run.app` URL. `adk deploy cloud_run`
copies the folder into a temp directory, generates a Dockerfile (Python 3.11 slim,
`google-adk` at your local version, your `requirements.txt`, a non-root user, and
`adk api_server` as the command), and runs `gcloud run deploy --source`, which builds the
image with Cloud Build and deploys the service.

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
- No secrets: the service calls Gemini through Agent Platform (formerly Vertex AI) as its
  service account. `greet_agent/.gcloudignore` keeps a local `.env` out of the image.

## Run it

Check the agent locally first:

1. `cd Module_15_Deployment/03_adk_deploy_cloud_run`
2. `cp greet_agent/.env.example greet_agent/.env` and fill in credentials for local use.
3. `adk web`, open http://localhost:8000, select `greet_agent`, and send "Greet Priya".
   (`adk run greet_agent` works too.)

Deploy (this creates a Cloud Run service and an Artifact Registry image):

1. `cd Module_15_Deployment/03_adk_deploy_cloud_run`
2. `export GCP_PROJECT=your-project-id`
3. `bash deploy.sh`

`deploy.sh` runs:

```bash
adk deploy cloud_run \
  --project="$GCP_PROJECT" \
  --region=us-central1 \
  --service_name=greet-agent \
  --with_ui \
  --env GOOGLE_CLOUD_LOCATION=global \
  ./greet_agent \
  -- --allow-unauthenticated
```

- Everything after `--` is passed to `gcloud run deploy` (for example
  `--no-allow-unauthenticated`, `--min-instances=1`, `--memory=2Gi`).
- ADK sets `GOOGLE_GENAI_USE_ENTERPRISE=1`, `GOOGLE_CLOUD_PROJECT`, and
  `GOOGLE_CLOUD_LOCATION=<region>` on the service. `--env GOOGLE_CLOUD_LOCATION=global`
  is there because `gemini-3.5-flash` is served from the `global` location, not from
  `us-central1`.
- `--allow-unauthenticated` makes the URL public so the UI opens in a browser. Remove it
  for anything real; topic 09 shows how to call a private service. If your organization
  blocks public services (domain restricted sharing), the deploy succeeds but the IAM
  step fails; deploy with `--no-allow-unauthenticated` instead.

## What to look for

```
Service [greet-agent] revision [greet-agent-00001-abc] has been deployed and is serving 100 percent of traffic.
Service URL: https://greet-agent-<hash>.us-central1.run.app
```

Because of `--with_ui`, the URL serves the ADK dev UI. Pick `greet_agent`, send "Greet
Priya", and check the tool call in the event view.

## `--with_ui` vs API only

| Mode | Flag | `/` | When |
|---|---|---|---|
| UI and API | `--with_ui` | ADK dev UI | Demos, internal tools, learning |
| API only | (omit) | no UI; `/run_sse`, `/apps/...` only | Production back ends |

Omit `--with_ui` for production. The dev UI is a debugging tool, not a customer-facing
front end, and it exposes session and trace inspection.

## Files

- `greet_agent/` - `__init__.py`, `agent.py`, `requirements.txt` (topic 04 layout), plus
  `.env.example` and a `.gcloudignore` that keeps a local `.env` out of the image.
- `deploy.sh` - the command above with defaults.

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| Build fails with `PERMISSION_DENIED` | Build service account has no build role | `../07_cloud_build_perms/` |
| `403` from the URL | Service requires authentication | Send an identity token (`../09_curl_deployed_agent/`) |
| `404 ... models/gemini-3.5-flash was not found` | Model location is the Cloud Run region | Keep `--env GOOGLE_CLOUD_LOCATION=global` |
| `403 ... aiplatform.endpoints.predict` | Runtime service account cannot call Agent Platform | Grant it `roles/aiplatform.user` |
| First request takes several seconds | Cold start with `min-instances=0` | `../10_autoscaling_tuning/` |

## Clean up

```bash
gcloud run services delete greet-agent --region=us-central1 --project="$GCP_PROJECT"
gcloud artifacts docker images delete \
  "us-central1-docker.pkg.dev/$GCP_PROJECT/cloud-run-source-deploy/greet-agent" \
  --delete-tags --project="$GCP_PROJECT"
```

The `cloud-run-source-deploy` repository is shared by every source deploy in the region;
delete it only if nothing else uses it. Locally: `rm -rf greet_agent/.env greet_agent/.adk`.
