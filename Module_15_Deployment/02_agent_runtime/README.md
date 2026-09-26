<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 02 - Agent Runtime

## What this shows

The shortest path from an agent folder to a managed endpoint. Agent Runtime (part of
Agent Platform, formerly Vertex AI; the API resource is still called a reasoning engine)
runs your agent with managed sessions, memory, scaling, and logging. You do not write a
Dockerfile or configure a service; `adk deploy agent_engine` packages `greet_agent/` and
creates the instance.

| You get | In practice |
|---|---|
| Managed sessions and Memory Bank | Conversation state is stored for you; the deployed server uses `agentengine://` sessions automatically. |
| Scaling | No instance counts to tune for a start. |
| Logging and tracing | Cloud Logging by default; `--otel_to_cloud` adds traces and metrics. |
| IAM auth | Calls go through the Agent Platform API with Google credentials; there is no public URL to forget to lock. |

| You give up | Why it matters |
|---|---|
| Control of the image | No system packages such as Node.js for stdio MCP servers. |
| A plain HTTPS URL | Clients call the Agent Platform API, not your own endpoint. |
| Portability | It is an Agent Platform resource, not a generic container. |

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)).
- The gcloud CLI, logged in twice (the second login is what `adk deploy` and the SDK use):

  ```bash
  gcloud auth login
  gcloud auth application-default login
  ```

- A Google Cloud project with billing enabled and the Agent Platform API on:

  ```bash
  export GCP_PROJECT=your-project-id
  gcloud services enable aiplatform.googleapis.com --project="$GCP_PROJECT"
  ```

- IAM for your own account: `roles/aiplatform.user` (create and call Agent Runtime
  instances). Owners and Editors already have it. To grant it:

  ```bash
  gcloud projects add-iam-policy-binding "$GCP_PROJECT" \
    --member="user:you@example.com" --role="roles/aiplatform.user"
  ```

- No service account to create: the instance runs as the Agent Platform Reasoning Engine
  service agent, `service-<PROJECT_NUMBER>@gcp-sa-aiplatform-re.iam.gserviceaccount.com`,
  which Google creates and grants model access to.
- Environment variables: `GCP_PROJECT` for `deploy.sh` (optional `GCP_REGION`, default
  `us-central1`, and `DISPLAY_NAME`). For `create_agent_engine.py`, copy `.env.example`
  in this folder to `.env` and set `GOOGLE_CLOUD_PROJECT` and `AGENT_RUNTIME_LOCATION`.
- Do not keep `GOOGLE_API_KEY` in `greet_agent/.env` when you deploy: `adk deploy
  agent_engine` copies every variable in that file onto the instance in plain text.
- Model location: see "Model location" below before you deploy.

## Run it

Check the agent locally first:

1. `cd Module_15_Deployment/02_agent_runtime`
2. `cp greet_agent/.env.example greet_agent/.env` and fill in credentials for local use.
3. `adk web`, open http://localhost:8000, select `greet_agent`, and send "Greet Priya".

Deploy (this creates a billable Agent Runtime instance):

1. `cd Module_15_Deployment/02_agent_runtime`
2. `export GCP_PROJECT=your-project-id`
3. `bash deploy.sh`

`deploy.sh` runs:

```bash
adk deploy agent_engine \
  --project="$GCP_PROJECT" \
  --region=us-central1 \
  --display_name="Greet Agent" \
  ./greet_agent
```

`--staging_bucket` from ADK 1.x is deprecated and ignored in ADK 2.x; you no longer need a
Cloud Storage bucket. To update an existing instance instead of creating a new one, add
`--agent_engine_id=<id>`.

`create_agent_engine.py` shows the other use: an empty instance, created with the Agent
Platform SDK, that only provides sessions and memory to an agent hosted elsewhere (for
example `adk web --session_service_uri=agentengine://<id>`). It is a setup script, not
an agent runner:

1. `cd Module_15_Deployment/02_agent_runtime`
2. `cp .env.example .env` and set `GOOGLE_CLOUD_PROJECT`.
3. `python create_agent_engine.py`

## What to look for

- The command prints the resource name,
  `projects/<number>/locations/us-central1/reasoningEngines/<id>`. The instance is
  listed in the Cloud Console under Agent Platform, Agent Runtime.
- In the Console you can open the instance and chat with it, or read its logs in Cloud
  Logging.

## Model location

The deployed agent gets `GOOGLE_CLOUD_LOCATION` set to the Agent Runtime region
(`us-central1` here), and the Gemini client uses that location. `gemini-3.5-flash` is
served from the `global` location, so a call from a `us-central1` instance can return
`404 NOT_FOUND` for the model. If you see that, either use a model served in your region
(for example `gemini-2.5-flash` in `us-central1`) or give the agent a model object that
pins its own location, as described in the `Gemini` class docstring in
`google/adk/models/google_llm.py` (subclass `Gemini` and return
`Client(enterprise=True, location="global")` from `api_client`).

## When to use Cloud Run instead

- You need extra system packages (Node.js for stdio MCP servers): topic 08.
- You want a plain HTTPS endpoint with your own auth in front: topic 03.
- You want scale-to-zero billing and full control over instance sizing: topic 10.

## Common errors

| Symptom | Cause |
|---|---|
| `PERMISSION_DENIED ... aiplatform.reasoningEngines.create` | Your account lacks `roles/aiplatform.user`. |
| `SERVICE_DISABLED` for `aiplatform.googleapis.com` | Enable the API (Prerequisites). |
| `404 NOT_FOUND` for the model when you query the instance | Model location; see above. |

## Clean up

Delete each instance you created. List them, then delete by id (`force=true` also
deletes its sessions and memories):

```bash
TOKEN=$(gcloud auth print-access-token)
BASE="https://us-central1-aiplatform.googleapis.com/v1/projects/$GCP_PROJECT/locations/us-central1/reasoningEngines"
curl -s -H "Authorization: Bearer $TOKEN" "$BASE" | grep '"name"'
curl -s -X DELETE -H "Authorization: Bearer $TOKEN" "$BASE/<id>?force=true"
```

Or delete it in the Cloud Console under Agent Platform, Agent Runtime. Remove the local
files with `rm -rf greet_agent/.env greet_agent/.adk .env`.
