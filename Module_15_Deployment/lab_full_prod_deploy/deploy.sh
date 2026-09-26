#!/usr/bin/env bash
# Author: Vishal Bulbule
# Date: 2026-09-22

# Lab 15: production deploy of greet_agent to Cloud Run in one pass.
#
#   1. Project setup: build permission, API key secret, trace permission.
#   2. Tests and eval gate; stop on any failure.
#   3. One `adk deploy cloud_run` with every production setting, so no revision
#      ever runs with weaker settings (public access, no secret) in between.
#
# Run:
#   export GCP_PROJECT=your-project-id
#   read -rs GOOGLE_API_KEY && export GOOGLE_API_KEY   # paste the key; it is not echoed
#   bash deploy.sh

set -euo pipefail

: "${GCP_PROJECT:?Set GCP_PROJECT to your Google Cloud project id}"
: "${GOOGLE_API_KEY:?Set GOOGLE_API_KEY to the key to store in Secret Manager}"

REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-greet-agent-prod}"
SECRET_NAME="${SECRET_NAME:-GOOGLE_API_KEY}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> [1/3] Project setup"
bash "$HERE/setup_secrets.sh"

echo "==> [2/3] Tests and eval gate"
(cd "$HERE" && pytest tests -v --tb=short)

echo "==> [3/3] Deploying $SERVICE_NAME"
# ADK flags:
#   --trace_to_cloud    export ADK spans to Cloud Trace (needs
#                       opentelemetry-exporter-gcp-trace in requirements.txt)
#   --env ...ENTERPRISE=FALSE  use the API key; adk deploy defaults to Agent Platform
# gcloud flags after `--`:
#   --no-allow-unauthenticated  callers need an identity token and run.invoker
#   --update-secrets            GOOGLE_API_KEY from Secret Manager, never in the image
#   scaling and sizing          see ../10_autoscaling_tuning/
adk deploy cloud_run \
  --project="$GCP_PROJECT" \
  --region="$REGION" \
  --service_name="$SERVICE_NAME" \
  --trace_to_cloud \
  --env GOOGLE_GENAI_USE_ENTERPRISE=FALSE \
  "$HERE/greet_agent" \
  -- \
  --no-allow-unauthenticated \
  --update-secrets="GOOGLE_API_KEY=${SECRET_NAME}:latest" \
  --min-instances=0 \
  --max-instances=10 \
  --concurrency=4 \
  --cpu=2 \
  --memory=2Gi

URL=$(gcloud run services describe "$SERVICE_NAME" \
  --project="$GCP_PROJECT" --region="$REGION" --format="value(status.url)")

echo
echo "Deployed: $URL"
echo "Verify with:"
echo "  URL=$URL bash $HERE/verify.sh"
