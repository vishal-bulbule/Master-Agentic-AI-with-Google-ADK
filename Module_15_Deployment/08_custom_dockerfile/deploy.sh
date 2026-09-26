#!/usr/bin/env bash
# Author: Vishal Bulbule
# Date: 2026-09-22

# Build this folder's Dockerfile with Cloud Build and deploy it to Cloud Run.
#
# `gcloud run deploy --source .` uploads the folder, builds the image from the
# Dockerfile, pushes it to Artifact Registry, and deploys it.
#
# Required:
#   GCP_PROJECT   your Google Cloud project id
# Optional:
#   GCP_REGION    Cloud Run region, default us-central1
#   SERVICE_NAME  default greet-agent-custom
#
# Run:
#   export GCP_PROJECT=your-project-id
#   bash deploy.sh

set -euo pipefail

: "${GCP_PROJECT:?Set GCP_PROJECT to your Google Cloud project id}"

REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-greet-agent-custom}"

echo "Deploying $SERVICE_NAME to Cloud Run: project=$GCP_PROJECT region=$REGION"

# The model runs on Agent Platform through the service's identity, so no API
# key is needed. gemini-3.5-flash is served from the global location, not from
# the Cloud Run region. The service is private: call it with an identity token
# (see ../09_curl_deployed_agent/).
gcloud run deploy "$SERVICE_NAME" \
  --project="$GCP_PROJECT" \
  --region="$REGION" \
  --source . \
  --no-allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --concurrency=4 \
  --min-instances=0 \
  --max-instances=10 \
  --set-env-vars="GOOGLE_GENAI_USE_ENTERPRISE=TRUE,GOOGLE_CLOUD_PROJECT=$GCP_PROJECT,GOOGLE_CLOUD_LOCATION=global"

URL="$(gcloud run services describe "$SERVICE_NAME" \
  --project="$GCP_PROJECT" --region="$REGION" --format='value(status.url)')"

echo
echo "Deployed: $URL"
echo "Try:"
echo "  curl -H \"Authorization: Bearer \$(gcloud auth print-identity-token)\" $URL/list-apps"
