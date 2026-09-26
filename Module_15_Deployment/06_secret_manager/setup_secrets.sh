#!/usr/bin/env bash
# Author: Vishal Bulbule
# Date: 2026-09-22

# Store a Gemini API key in Secret Manager and expose it to a Cloud Run service.
#
#   1. Create the secret, or add a new version if it exists.
#   2. Grant the service's runtime service account read access to it.
#   3. Mount it as the GOOGLE_API_KEY env var on the service, and switch the
#      service to the API key path (GOOGLE_GENAI_USE_ENTERPRISE=FALSE), because
#      `adk deploy cloud_run` sets GOOGLE_GENAI_USE_ENTERPRISE=1 by default.
#
# The key is read from the environment and piped to gcloud on stdin, so it never
# appears in shell history, process arguments, or files.
#
# Run:
#   export GCP_PROJECT=your-project-id
#   read -rs GOOGLE_API_KEY && export GOOGLE_API_KEY   # paste the key, press Enter
#   export SERVICE_NAME=greet-agent                    # optional, default greet-agent
#   bash setup_secrets.sh

set -euo pipefail

: "${GCP_PROJECT:?Set GCP_PROJECT to your Google Cloud project id}"
: "${GOOGLE_API_KEY:?Set GOOGLE_API_KEY to the key you want to store}"

REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-greet-agent}"
SECRET_NAME="${SECRET_NAME:-GOOGLE_API_KEY}"

# The default runtime identity of Cloud Run services. If your service runs as a
# dedicated service account, set RUNTIME_SA to its email instead.
PROJECT_NUM=$(gcloud projects describe "$GCP_PROJECT" --format="value(projectNumber)")
RUNTIME_SA="${RUNTIME_SA:-${PROJECT_NUM}-compute@developer.gserviceaccount.com}"

echo "[1/3] Storing secret $SECRET_NAME in $GCP_PROJECT"
if gcloud secrets describe "$SECRET_NAME" --project="$GCP_PROJECT" >/dev/null 2>&1; then
  printf "%s" "$GOOGLE_API_KEY" | gcloud secrets versions add "$SECRET_NAME" \
    --project="$GCP_PROJECT" --data-file=-
else
  printf "%s" "$GOOGLE_API_KEY" | gcloud secrets create "$SECRET_NAME" \
    --project="$GCP_PROJECT" --replication-policy=automatic --data-file=-
fi

echo "[2/3] Granting $RUNTIME_SA read access to $SECRET_NAME"
# Bound on the secret, not the project, so the account can read only this secret.
gcloud secrets add-iam-policy-binding "$SECRET_NAME" \
  --project="$GCP_PROJECT" \
  --member="serviceAccount:$RUNTIME_SA" \
  --role="roles/secretmanager.secretAccessor" \
  --condition=None \
  --format=none

echo "[3/3] Mounting the secret on Cloud Run service $SERVICE_NAME"
if gcloud run services describe "$SERVICE_NAME" --project="$GCP_PROJECT" --region="$REGION" >/dev/null 2>&1; then
  gcloud run services update "$SERVICE_NAME" \
    --project="$GCP_PROJECT" \
    --region="$REGION" \
    --update-secrets="GOOGLE_API_KEY=${SECRET_NAME}:latest" \
    --update-env-vars="GOOGLE_GENAI_USE_ENTERPRISE=FALSE"
else
  echo "Service $SERVICE_NAME does not exist yet. Deploy it with these flags instead:"
  echo "  adk deploy cloud_run ... --env GOOGLE_GENAI_USE_ENTERPRISE=FALSE ./greet_agent \\"
  echo "    -- --update-secrets=GOOGLE_API_KEY=${SECRET_NAME}:latest"
fi

echo
echo "Check that the env var references the secret (the value is not shown):"
echo "  gcloud run services describe $SERVICE_NAME --region=$REGION --format=yaml | grep -A4 GOOGLE_API_KEY"
