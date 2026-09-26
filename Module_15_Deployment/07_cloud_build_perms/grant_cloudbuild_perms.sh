#!/usr/bin/env bash
# Author: Vishal Bulbule
# Date: 2026-09-22

# Grant the default compute service account the role Cloud Build needs for
# source deploys (`adk deploy cloud_run`, `gcloud run deploy --source .`).
#
# On projects created with current defaults, Cloud Build runs source builds as
# the default compute service account, and that account has no build role. The
# deploy then fails with a 403 on the build step.
#
# roles/cloudbuild.builds.builder covers running the build, reading the
# uploaded source, pushing the image to Artifact Registry, and writing build
# logs. Nothing else is granted: the same account is the runtime identity of
# your Cloud Run services by default, so keep it narrow.
#
# Safe to run more than once.
#
# Run:
#   export GCP_PROJECT=your-project-id
#   bash grant_cloudbuild_perms.sh

set -euo pipefail

: "${GCP_PROJECT:?Set GCP_PROJECT to your Google Cloud project id}"

PROJECT_NUM=$(gcloud projects describe "$GCP_PROJECT" --format="value(projectNumber)")
SA="${PROJECT_NUM}-compute@developer.gserviceaccount.com"

echo "Granting roles/cloudbuild.builds.builder to $SA in $GCP_PROJECT"

gcloud projects add-iam-policy-binding "$GCP_PROJECT" \
  --member="serviceAccount:$SA" \
  --role="roles/cloudbuild.builds.builder" \
  --condition=None \
  --format=none

echo "Done. IAM changes can take a minute to apply; then retry the deploy."
