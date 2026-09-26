#!/usr/bin/env bash
# Author: Vishal Bulbule
# Date: 2026-09-22

# Lab 15: one-time project setup for the production deploy.
#
#   1. Cloud Build permission for source deploys (topic 07).
#   2. The GOOGLE_API_KEY secret, readable only by the runtime service account (topic 06).
#   3. Cloud Trace write access for the runtime service account, used by
#      `adk deploy cloud_run --trace_to_cloud`.
#
# Safe to run more than once: an existing secret gets a new version.
#
# Run:
#   export GCP_PROJECT=your-project-id
#   read -rs GOOGLE_API_KEY && export GOOGLE_API_KEY   # paste the key; it is not echoed
#   bash setup_secrets.sh

set -euo pipefail

: "${GCP_PROJECT:?Set GCP_PROJECT to your Google Cloud project id}"
: "${GOOGLE_API_KEY:?Set GOOGLE_API_KEY to the key to store in Secret Manager}"

SECRET_NAME="${SECRET_NAME:-GOOGLE_API_KEY}"
PROJECT_NUM=$(gcloud projects describe "$GCP_PROJECT" --format="value(projectNumber)")
# Builds and the service both run as the default compute service account here.
# For separate identities, see ../07_cloud_build_perms/README.md.
SA="${PROJECT_NUM}-compute@developer.gserviceaccount.com"

echo "[1/3] Cloud Build permission for $SA"
gcloud projects add-iam-policy-binding "$GCP_PROJECT" \
  --member="serviceAccount:$SA" --role="roles/cloudbuild.builds.builder" \
  --condition=None --format=none

echo "[2/3] Secret $SECRET_NAME"
if gcloud secrets describe "$SECRET_NAME" --project="$GCP_PROJECT" >/dev/null 2>&1; then
  printf "%s" "$GOOGLE_API_KEY" | gcloud secrets versions add "$SECRET_NAME" \
    --project="$GCP_PROJECT" --data-file=-
else
  printf "%s" "$GOOGLE_API_KEY" | gcloud secrets create "$SECRET_NAME" \
    --project="$GCP_PROJECT" --replication-policy=automatic --data-file=-
fi
gcloud secrets add-iam-policy-binding "$SECRET_NAME" \
  --project="$GCP_PROJECT" \
  --member="serviceAccount:$SA" --role="roles/secretmanager.secretAccessor" \
  --condition=None --format=none

echo "[3/3] Cloud Trace write access for $SA"
gcloud projects add-iam-policy-binding "$GCP_PROJECT" \
  --member="serviceAccount:$SA" --role="roles/cloudtrace.agent" \
  --condition=None --format=none

echo "Project setup done."
