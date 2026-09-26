<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 15: Deployment

Every earlier module ran agents on `localhost`. This module takes one small agent to
Google Cloud: Agent Runtime or Cloud Run, configuration and secrets, permissions,
calling the private service, scaling settings, and a CI pipeline that refuses to deploy
when the eval fails.

The agent (`greet_agent`) is deliberately trivial so the deployment is what you look at.

## Topics

Follow them in order.

| Folder | What it shows |
|---|---|
| [`01_deployment_options_table/`](01_deployment_options_table/) | Agent Runtime vs Cloud Run vs GKE vs self-hosted, and the questions that decide it |
| [`02_agent_runtime/`](02_agent_runtime/) | `adk deploy agent_engine`, and an empty instance for sessions and memory |
| [`03_adk_deploy_cloud_run/`](03_adk_deploy_cloud_run/) | `adk deploy cloud_run` in one command, with and without the dev UI |
| [`04_required_project_structure/`](04_required_project_structure/) | The agent folder layout every `adk` command expects, and keeping `.env` out of images |
| [`05_env_vars/`](05_env_vars/) | The variables an agent needs and what `adk deploy` sets for you |
| [`06_secret_manager/`](06_secret_manager/) | Storing an API key in Secret Manager and mounting it on Cloud Run |
| [`07_cloud_build_perms/`](07_cloud_build_perms/) | The IAM binding a first source deploy needs |
| [`08_custom_dockerfile/`](08_custom_dockerfile/) | Your own image and FastAPI app with `get_fast_api_app`, deployed with `gcloud run deploy --source` |
| [`09_curl_deployed_agent/`](09_curl_deployed_agent/) | Identity tokens, creating a session, and `/run_sse` |
| [`10_autoscaling_tuning/`](10_autoscaling_tuning/) | Instances, concurrency, CPU, and memory for agent workloads |
| [`11_github_actions_cicd/`](11_github_actions_cicd/) | Eval-gated GitHub Actions pipeline with Workload Identity Federation |
| [`lab_full_prod_deploy/`](lab_full_prod_deploy/) | Lab: private service, secret, scaling limits, traces, and CI in one deploy |

Topics 01, 05, and 10 are reading only. The others have scripts that create resources
in your project; each README says so before the command.

## Before you start

Local (every topic runs its agent locally first with `adk web`):

- Repository setup: [SETUP.md](../SETUP.md). The root `requirements.txt` covers the
  local runs and the pytest eval gates; CI installs `requirements-dev.txt` instead.
- Each agent folder has a `.env.example`; copy it to `.env` in the same folder for local
  runs. The `.gcloudignore` files keep that `.env` out of deployed images (topic 04).

Google Cloud (topics 02, 03, 06 to 11, and the lab create resources; 01, 04, 05, and 10
are reading or local only):

- gcloud CLI, logged in with `gcloud auth login` and `gcloud auth application-default login`.
- A project with billing and these APIs:

  ```bash
  gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
    artifactregistry.googleapis.com secretmanager.googleapis.com \
    aiplatform.googleapis.com cloudtrace.googleapis.com
  ```

- Your account: Owner, or `roles/run.sourceDeveloper`, `roles/serviceusage.serviceUsageConsumer`,
  `roles/iam.serviceAccountUser` on the runtime service account, `roles/aiplatform.user`
  (Agent Runtime), `roles/secretmanager.admin` (topic 06 and the lab), and
  `roles/resourcemanager.projectIamAdmin` (IAM bindings in topics 07 and the lab). Each
  topic README lists the exact grant commands.
- The default compute service account (build and runtime identity):
  `roles/cloudbuild.builds.builder` (topic 07), `roles/aiplatform.user` (topic 03),
  plus `roles/secretmanager.secretAccessor` and `roles/cloudtrace.agent` in the lab.
- Secret Manager: one secret, `GOOGLE_API_KEY`, created by topic 06 and the lab.
- CI (topic 11 and the lab): a GitHub repository, a `deployer` service account, and a
  Workload Identity Federation pool and provider; topic 11 has the commands. Also enable
  `iam.googleapis.com`, `iamcredentials.googleapis.com`, and `sts.googleapis.com`.
- Docker, only to build the topic 08 image locally.

## What `adk deploy cloud_run` sets on the service

ADK 2.9.2 sets `GOOGLE_GENAI_USE_ENTERPRISE=1` (Gemini through Agent Platform, formerly
Vertex AI, using the service account), `GOOGLE_CLOUD_PROJECT`, and
`GOOGLE_CLOUD_LOCATION` equal to the Cloud Run region. `gemini-3.5-flash` is served from
the `global` location, so the deploy commands in this module add
`--env GOOGLE_CLOUD_LOCATION=global`. Topic 05 has the details.

## Cost

Check current prices on the Cloud Run, Agent Platform, Secret Manager, and Cloud Build
pricing pages; the shape of the cost is:

- Cloud Run bills for CPU and memory while instances run (and all the time with
  `min-instances` above 0 or CPU always allocated), with a monthly free tier. A demo
  agent with a few hundred requests a month stays inside it.
- `--min-instances=1` keeps one instance billed around the clock. Use it only where cold
  starts hurt users (topic 10).
- Model calls are billed per token and are usually the largest item for a real agent.
  Flash models cost a fraction of Pro models; start with Flash.
- Secret Manager bills per active secret version and per access, which is negligible at
  this scale.
- Cloud Build has a daily free allowance of build minutes.

## Cold starts

With `min-instances=0` (the default), the first request after an idle period waits for a
container to start and Python to import ADK and its dependencies, typically a few
seconds. If that is not acceptable for your users, keep one instance warm or enable
startup CPU boost; otherwise accept it. Topic 10 covers the trade-off.

## Clean up

Each topic README ends with the exact commands for what it created. All together:

```bash
gcloud run services delete greet-agent --region=us-central1
gcloud run services delete greet-agent-custom --region=us-central1
gcloud run services delete greet-agent-prod --region=us-central1
gcloud secrets delete GOOGLE_API_KEY
gcloud artifacts repositories delete cloud-run-source-deploy --location=us-central1
```

Delete the Artifact Registry repository only if nothing else in the project deploys from
source. Agent Runtime instances: see the Clean up section of `02_agent_runtime/`. IAM
bindings, the deployer service account, and the Workload Identity pool: see
`07_cloud_build_perms/`, `11_github_actions_cicd/`, and `lab_full_prod_deploy/`.
