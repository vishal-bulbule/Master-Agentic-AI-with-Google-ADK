<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 05 - Environment Variables

## What this shows

Cloud Run and Agent Runtime take configuration from environment variables. This page
lists the ones an ADK agent needs, how `adk deploy` sets them, and how to set them
yourself with `gcloud`.

## Prerequisites

- Reading only, except the `gcloud` commands, which need:
  - the `greet-agent` service from `../03_adk_deploy_cloud_run/` deployed;
  - the gcloud CLI logged in (`gcloud auth login`) with `roles/run.viewer` to describe
    the service, or `roles/run.developer` plus `roles/iam.serviceAccountUser` on the
    runtime service account to change it:

    ```bash
    gcloud projects add-iam-policy-binding "$GCP_PROJECT" \
      --member="user:you@example.com" --role="roles/run.developer"
    ```

## Run it

Nothing to deploy here. To see what `adk deploy cloud_run` set on the topic 03 service:

1. `gcloud run services describe greet-agent --region=us-central1 --format="yaml(spec.template.spec.containers[0].env)"`

## What to look for

You should see `GOOGLE_GENAI_USE_ENTERPRISE`, `GOOGLE_CLOUD_PROJECT`, and
`GOOGLE_CLOUD_LOCATION` (`global`, from `--env`), and no secret values.

## The variables

| Variable | Purpose |
|---|---|
| `GOOGLE_GENAI_USE_ENTERPRISE` | `TRUE`: call Gemini through Agent Platform (formerly Vertex AI) with Google credentials. `FALSE`: use a Gemini API key. |
| `GOOGLE_API_KEY` | Gemini API key. Only for `GOOGLE_GENAI_USE_ENTERPRISE=FALSE`. Put it in Secret Manager (topic 06). |
| `GOOGLE_CLOUD_PROJECT` | Project for Agent Platform calls. |
| `GOOGLE_CLOUD_LOCATION` | Agent Platform location for model calls. `gemini-3.5-flash` is served from `global`. |

`GOOGLE_GENAI_USE_ENTERPRISE` replaces `GOOGLE_GENAI_USE_VERTEXAI`, which still works in
google-genai 2.x but prints a deprecation warning. If both are set with different values,
`GOOGLE_GENAI_USE_ENTERPRISE` wins.

## API key vs Agent Platform

| | API key | Agent Platform |
|---|---|---|
| Set | `GOOGLE_GENAI_USE_ENTERPRISE=FALSE` | `GOOGLE_GENAI_USE_ENTERPRISE=TRUE` |
| Auth | `GOOGLE_API_KEY` | Application Default Credentials: on Cloud Run, the service's service account |
| Key to manage | Yes | No |
| Needs project and location | No | Yes |
| Billing | The key's project | The Google Cloud project |
| Good for | Local development, quick tests | Production on Google Cloud |

On Cloud Run, prefer Agent Platform: grant the service's service account
`roles/aiplatform.user` and no key changes hands.

## What `adk deploy cloud_run` sets for you

Checked against the ADK 2.9.2 source (`cli/deployers/_cloud_run_deployer.py`):

- It sets `GOOGLE_GENAI_USE_ENTERPRISE=1`, `GOOGLE_CLOUD_PROJECT` (from `--project`),
  and `GOOGLE_CLOUD_LOCATION` (from `--region`) on the service.
- `--env KEY=VALUE` (repeatable) adds variables and overrides those defaults. The
  Cloud Run region and the model location are different things, so for
  `gemini-3.5-flash` on Agent Platform pass `--env GOOGLE_CLOUD_LOCATION=global`.
- A `.env` in the agent folder is read only for `GOOGLE_CLOUD_PROJECT` and
  `GOOGLE_CLOUD_LOCATION`, as fallbacks for `--project` and `--region`. Its other values
  are not set as service env vars.
- But the `.env` file itself is copied into the image with the rest of the folder,
  unless the agent folder has a `.gitignore`, `.gcloudignore`, or `.ae_ignore` that
  excludes it, and the ADK server loads it at startup. The agent folders in this module
  ship a `.gcloudignore` that excludes `.env` for that reason.
- ADK manages `--update-env-vars` itself, so you cannot pass it (or `--set-env-vars`)
  through to gcloud. Use `--env`.

```bash
adk deploy cloud_run \
  --project="$GCP_PROJECT" \
  --region=us-central1 \
  --service_name=greet-agent \
  --env GOOGLE_CLOUD_LOCATION=global \
  ./greet_agent
```

`adk deploy agent_engine` is different: it reads every variable in the agent folder's
`.env` and sets them on the Agent Runtime instance, including `GOOGLE_API_KEY` if it is
there. Keep keys out of that file when you deploy to Agent Runtime.

## Setting env vars with gcloud

For services deployed with `gcloud run deploy` (topic 08):

```bash
gcloud run deploy greet-agent-custom \
  --source . \
  --region=us-central1 \
  --set-env-vars=GOOGLE_GENAI_USE_ENTERPRISE=TRUE,GOOGLE_CLOUD_PROJECT=your-project-id,GOOGLE_CLOUD_LOCATION=global
```

Values with commas or spaces are easier in a YAML file:

```bash
gcloud run deploy greet-agent-custom --source . --region=us-central1 --env-vars-file=env.yaml
```

```yaml
# env.yaml
GOOGLE_GENAI_USE_ENTERPRISE: "TRUE"
GOOGLE_CLOUD_PROJECT: your-project-id
GOOGLE_CLOUD_LOCATION: global
```

Change or remove variables on a running service (each change creates a new revision):

```bash
gcloud run services update greet-agent --region=us-central1 \
  --update-env-vars=GOOGLE_CLOUD_LOCATION=global

gcloud run services update greet-agent --region=us-central1 \
  --remove-env-vars=OBSOLETE_VAR
```

## Never put secrets here

Env var values set with `--env`, `--set-env-vars`, or `--update-env-vars` are plain text
in the service description, readable by anyone with `roles/run.viewer`. That is fine for
a project id, not for `GOOGLE_API_KEY`. Use Secret Manager (topic 06).

## Clean up

Each `services update` creates a revision; nothing else is created. To undo a variable
you added: `gcloud run services update greet-agent --region=us-central1 --remove-env-vars=NAME`.
