<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab 15 - Production Deploy

## What this shows

A Cloud Run deploy with what a production service needs, from one script: the API key
in Secret Manager, IAM-only access, scaling limits, an eval gate before every deploy,
traces in Cloud Trace, and the same steps in CI.

| Requirement | How this lab meets it |
|---|---|
| No secret in the image or service config | `setup_secrets.sh` stores `GOOGLE_API_KEY` in Secret Manager; the deploy mounts it with `--update-secrets`; `greet_agent/.gcloudignore` keeps a local `.env` out of the image |
| Authenticated access only | `--no-allow-unauthenticated`; callers need `roles/run.invoker` |
| Scaling limits | min 0, max 10 instances, concurrency 4, 2 vCPU, 2 GiB (topic 10) |
| Eval gate | `pytest tests` (unit tests and a two-case eval) runs before the deploy, locally and in CI |
| Traces | `adk deploy cloud_run --trace_to_cloud`; the runtime service account has `roles/cloudtrace.agent` |

All production settings go into a single `adk deploy cloud_run` call (gcloud flags after
`--`). Do not deploy first and tighten settings with
`gcloud run services update` afterwards: that leaves a window where a public revision
without the secret is serving, and `services update` has no
`--no-allow-unauthenticated` flag.

```
lab_full_prod_deploy/
|-- deploy.sh               setup, tests, deploy
|-- setup_secrets.sh        build permission, secret, trace permission
|-- verify.sh               checks anonymous calls fail and an authenticated call works
|-- conftest.py
|-- requirements-dev.txt    what the tests and CI need
|-- greet_agent/            agent, requirements.txt (adds the Cloud Trace exporter), .gcloudignore
|-- tests/                  unit tests, eval gate, greet.test.json, test_config.json
`-- .github/workflows/deploy.yml
```

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)), or `pip install -r requirements-dev.txt`
  for the local test gate.
- The gcloud CLI logged in twice (the second login is what the local eval gate uses):

  ```bash
  gcloud auth login
  gcloud auth application-default login
  export GCP_PROJECT=your-project-id
  gcloud config set project "$GCP_PROJECT"
  ```

- APIs:

  ```bash
  gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
    artifactregistry.googleapis.com secretmanager.googleapis.com \
    aiplatform.googleapis.com cloudtrace.googleapis.com --project="$GCP_PROJECT"
  ```

- IAM for your own account (Owners have all of these): `roles/run.sourceDeveloper`,
  `roles/serviceusage.serviceUsageConsumer`, `roles/secretmanager.admin`,
  `roles/resourcemanager.projectIamAdmin` (for the bindings `setup_secrets.sh` makes), and
  `roles/iam.serviceAccountUser` on the runtime service account:

  ```bash
  ME="user:you@example.com"
  PROJECT_NUM=$(gcloud projects describe "$GCP_PROJECT" --format="value(projectNumber)")
  for ROLE in roles/run.sourceDeveloper roles/serviceusage.serviceUsageConsumer \
              roles/secretmanager.admin roles/resourcemanager.projectIamAdmin; do
    gcloud projects add-iam-policy-binding "$GCP_PROJECT" --member="$ME" --role="$ROLE"
  done
  gcloud iam service-accounts add-iam-policy-binding \
    "${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
    --member="$ME" --role="roles/iam.serviceAccountUser"
  ```

- Service account: builds and the service run as the default compute service account.
  `setup_secrets.sh` grants it `roles/cloudbuild.builds.builder`,
  `roles/secretmanager.secretAccessor` on the secret, and `roles/cloudtrace.agent`.
- Secret: a Gemini API key from https://aistudio.google.com/apikey, read into
  `GOOGLE_API_KEY` in your shell. `setup_secrets.sh` stores it as the Secret Manager
  secret `GOOGLE_API_KEY`.
- Local eval gate credentials: copy `greet_agent/.env.example` to `greet_agent/.env` and
  fill it in. `greet_agent/.gcloudignore` keeps it out of the image.
- For CI: the Workload Identity Federation pool, deployer service account, and repository
  variables from `../11_github_actions_cicd/README.md`. The deployer also needs
  `roles/iam.serviceAccountUser` on the compute service account (topic 11 grants it).

## Run it

This creates a secret, IAM bindings, an image, and a Cloud Run service in your project.

1. `cd Module_15_Deployment/lab_full_prod_deploy`
2. `export GCP_PROJECT=your-project-id`
3. `read -rs GOOGLE_API_KEY && export GOOGLE_API_KEY` (paste the key; it is not echoed)
4. `bash deploy.sh`

Before deploying you can chat with the agent locally: `adk web` from this folder, select
`greet_agent`, send "Greet Priya".

The deployed service uses the API key from Secret Manager
(`GOOGLE_GENAI_USE_ENTERPRISE=FALSE`, set with `--env` because `adk deploy` defaults to
Agent Platform). The simpler production option is to skip the key and let the service
account call Agent Platform (formerly Vertex AI): drop the `--env` and `--update-secrets`
flags, add `--env GOOGLE_CLOUD_LOCATION=global`, and grant the runtime service account
`roles/aiplatform.user`. The lab keeps the key to practice the Secret Manager path, which
you need anyway for third-party API keys.

## What to look for

Verify the deployed service:

```bash
URL=$(gcloud run services describe greet-agent-prod --region=us-central1 --format="value(status.url)")
URL=$URL bash verify.sh
```

Expected:

- The anonymous request gets `401` or `403`.
- The session is created.
- `/run_sse` returns events ending with the text `Hello, Priya!`.

Then open Trace Explorer in the Cloud Console and filter on the service. Each request
shows `invoke_agent`, `generate_content`, and `execute_tool greet` spans. If nothing
appears after a minute, check that `roles/cloudtrace.agent` is bound to the runtime
service account and read the service logs for exporter errors.

## CI

1. Do the one-time Workload Identity Federation and deployer setup in
   `../11_github_actions_cicd/README.md`, and set the `GCP_PROJECT`, `WIF_PROVIDER`, and
   `DEPLOYER_SA` repository variables.
2. Run `setup_secrets.sh` once. CI does not create secrets or IAM bindings.
3. Copy `.github/workflows/deploy.yml` to `.github/workflows/` at the repository root.
4. Push a change under this folder to `main`. The job runs the tests, then deploys.

To see the gate work, change the expected answer in `tests/greet.test.json` to
`Hello, somebody else!` and push: the test step fails and the deploy step is skipped.

## What you end up with

- A private Cloud Run service, `greet-agent-prod`.
- The API key only in Secret Manager.
- Scaling capped at 10 instances of 2 vCPU and 2 GiB, 4 concurrent requests each.
- Traces in Cloud Trace.
- A pipeline that deploys only after the eval passes.

The same setup works for any agent in this repository: replace `greet_agent/` and the
eval cases in `tests/`.

## Clean up

```bash
PROJECT_NUM=$(gcloud projects describe "$GCP_PROJECT" --format="value(projectNumber)")
SA="${PROJECT_NUM}-compute@developer.gserviceaccount.com"

gcloud run services delete greet-agent-prod --region=us-central1 --project="$GCP_PROJECT"
gcloud artifacts docker images delete \
  "us-central1-docker.pkg.dev/$GCP_PROJECT/cloud-run-source-deploy/greet-agent-prod" \
  --delete-tags --project="$GCP_PROJECT"
gcloud secrets delete GOOGLE_API_KEY --project="$GCP_PROJECT"
for ROLE in roles/cloudtrace.agent roles/cloudbuild.builds.builder; do
  gcloud projects remove-iam-policy-binding "$GCP_PROJECT" \
    --member="serviceAccount:$SA" --role="$ROLE"
done
unset GOOGLE_API_KEY
```

Keep `roles/cloudbuild.builds.builder` if other topics still deploy from source. For the
CI resources (pool, deployer account), see the Clean up section of
`../11_github_actions_cicd/README.md`.
