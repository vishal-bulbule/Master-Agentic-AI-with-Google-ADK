#!/usr/bin/env bash
# Author: Vishal Bulbule
# Date: 2026-09-22

# Deploy ./greet_agent to Cloud Run with `adk deploy cloud_run`.
#
# ADK generates a Dockerfile, builds the image with Cloud Build, and deploys a
# Cloud Run service. Arguments after `--` are passed to `gcloud run deploy`.
#
# Required:
#   GCP_PROJECT   your Google Cloud project id
# Optional:
#   GCP_REGION    Cloud Run region, default us-central1
#   SERVICE_NAME  default greet-agent
#
# Run:
#   export GCP_PROJECT=your-project-id
#   bash deploy.sh

set -euo pipefail

: "${GCP_PROJECT:?Set GCP_PROJECT to your Google Cloud project id}"

REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-greet-agent}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Deploying greet_agent to Cloud Run: project=$GCP_PROJECT region=$REGION service=$SERVICE_NAME"

# --with_ui serves the ADK dev UI next to the API; drop it for an API-only service.
# The model runs on Agent Platform through the service account (ADK sets
# GOOGLE_GENAI_USE_ENTERPRISE=1). GOOGLE_CLOUD_LOCATION defaults to the Cloud Run
# region, but gemini-3.5-flash is served from the global location.
# --allow-unauthenticated makes the URL public so the UI opens in a browser.
# Use --no-allow-unauthenticated for anything real (topic 09, lab).
adk deploy cloud_run \
  --project="$GCP_PROJECT" \
  --region="$REGION" \
  --service_name="$SERVICE_NAME" \
  --with_ui \
  --env GOOGLE_CLOUD_LOCATION=global \
  "$HERE/greet_agent" \
  -- --allow-unauthenticated

echo "Done. Open the Service URL printed above."
echo "If the build failed with a permission error, see ../07_cloud_build_perms/."
