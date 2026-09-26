<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 06 - Secrets via Secret Manager

## What this shows

Plain env vars are fine for non-secret config such as `GOOGLE_CLOUD_PROJECT`. They are
not fine for API keys, OAuth client secrets, database passwords, or third-party tokens.
Those go in Secret Manager, and Cloud Run injects them into the container at start.

Signs of doing it wrong:

- a `.env` file with a real key committed to git;
- a Dockerfile with `ENV GOOGLE_API_KEY=...`;
- `--set-env-vars=GOOGLE_API_KEY=...` on a deploy: the value is then readable by
  anyone with `roles/run.viewer` on the project.

Treat the image and the service description as public. Anyone who can pull the image
can read files in it.

Before adding a key at all: on Cloud Run the simplest option is Agent Platform (formerly
Vertex AI) with the service's own service account (`roles/aiplatform.user`). No key
exists, so none can leak. Use Secret Manager for keys you cannot avoid: a Gemini API key
if you use that path, or tokens for third-party APIs your tools call.

## Prerequisites

- The `greet-agent` Cloud Run service from `../03_adk_deploy_cloud_run/` (the script
  mounts the secret on it; if it does not exist yet, the script prints the deploy flags to
  use instead).
- The gcloud CLI logged in (`gcloud auth login`) and the Secret Manager API on:

  ```bash
  export GCP_PROJECT=your-project-id
  gcloud services enable secretmanager.googleapis.com --project="$GCP_PROJECT"
  ```

- IAM for your own account: `roles/secretmanager.admin` (create the secret and set its
  IAM policy), `roles/run.developer` (update the service), and `roles/iam.serviceAccountUser`
  on the runtime service account (topic 03 grants the last one):

  ```bash
  for ROLE in roles/secretmanager.admin roles/run.developer; do
    gcloud projects add-iam-policy-binding "$GCP_PROJECT" \
      --member="user:you@example.com" --role="$ROLE"
  done
  ```

- A Gemini API key from https://aistudio.google.com/apikey, read into `GOOGLE_API_KEY`
  in your shell (step 3 of Run it). The script grants
  `roles/secretmanager.secretAccessor` on the secret to the runtime service account,
  `<PROJECT_NUMBER>-compute@developer.gserviceaccount.com`; set `RUNTIME_SA` if the
  service runs as a different account.

## Run it

This creates a secret and changes IAM and the service in your project.

1. `cd Module_15_Deployment/06_secret_manager`
2. `export GCP_PROJECT=your-project-id`
3. `read -rs GOOGLE_API_KEY && export GOOGLE_API_KEY` (paste the key; it is not echoed)
4. `export SERVICE_NAME=greet-agent` (the service from topic 03)
5. `bash setup_secrets.sh`

## What to look for

```bash
gcloud run services describe greet-agent --region=us-central1 --format=yaml | grep -A4 GOOGLE_API_KEY
```

The env var shows a `secretKeyRef` (secret name and version), not the value.

When a new instance starts, Cloud Run reads the secret version as the service's runtime
service account and sets the env var in the container. The value is never written into
the image or the service description.

## The three steps

```bash
# 1. Create the secret (the value comes from stdin, not the command line)
printf "%s" "$GOOGLE_API_KEY" | gcloud secrets create GOOGLE_API_KEY --data-file=-

# 2. Let the service's runtime service account read it
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY \
  --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# 3. Mount it as an env var on the service
gcloud run services update greet-agent \
  --update-secrets=GOOGLE_API_KEY=GOOGLE_API_KEY:latest \
  --update-env-vars=GOOGLE_GENAI_USE_ENTERPRISE=FALSE
```

`GOOGLE_GENAI_USE_ENTERPRISE=FALSE` matters: `adk deploy cloud_run` sets
`GOOGLE_GENAI_USE_ENTERPRISE=1` on the service by default, and with that set the Gemini
client uses Agent Platform and ignores `GOOGLE_API_KEY`.

`setup_secrets.sh` runs the three steps with the project-number lookup, and adds a new
version instead of failing when the secret already exists.

## Pin a version in production

```bash
--update-secrets=GOOGLE_API_KEY=GOOGLE_API_KEY:3
```

With `:latest`, a new secret version reaches instances as they start, without a deploy,
and different instances can run different versions for a while. Pinning a number makes a
key rotation a deploy you can review and roll back.

## More

- Several secrets: `--update-secrets=A=A:latest,B=B:latest`.
- Mount as a file instead of an env var: `--update-secrets=/secrets/db_password=DB_PASSWORD:latest`.

## Common errors

| Error | Cause |
|---|---|
| `Permission 'secretmanager.versions.access' denied` | Step 2 missing, or granted to a different service account than the one the service runs as. |
| `Secret ... not found` | The secret was created in a different project. |
| Agent uses Agent Platform instead of the key | `GOOGLE_GENAI_USE_ENTERPRISE` is still `1`. |
| Env var still old after rotation | Instances started before the new version still hold the old value; deploy a new revision. |

## Clean up

Put the service back on Agent Platform, then delete the secret (its IAM binding goes
with it):

```bash
gcloud run services update greet-agent --region=us-central1 \
  --remove-secrets=GOOGLE_API_KEY --update-env-vars=GOOGLE_GENAI_USE_ENTERPRISE=TRUE
gcloud secrets delete GOOGLE_API_KEY --project="$GCP_PROJECT"
unset GOOGLE_API_KEY
```
