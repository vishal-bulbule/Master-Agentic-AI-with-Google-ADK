#!/usr/bin/env bash
# Author: Vishal Bulbule
# Date: 2026-09-22

# Deploy ./greet_agent to Agent Runtime with `adk deploy agent_engine`.
#
# No Dockerfile and no service to configure: the CLI packages the folder, and
# Agent Runtime builds and runs it with managed sessions and memory.
#
# Required:
#   GCP_PROJECT   your Google Cloud project id
# Optional:
#   GCP_REGION    Agent Runtime region, default us-central1
#   DISPLAY_NAME  default "Greet Agent"
#
# Run:
#   export GCP_PROJECT=your-project-id
#   bash deploy.sh

set -euo pipefail

: "${GCP_PROJECT:?Set GCP_PROJECT to your Google Cloud project id}"

REGION="${GCP_REGION:-us-central1}"
DISPLAY_NAME="${DISPLAY_NAME:-Greet Agent}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Deploying greet_agent to Agent Runtime: project=$GCP_PROJECT region=$REGION"

# ADK 1.x needed --staging_bucket; ADK 2.x ignores it, so it is not passed.
adk deploy agent_engine \
  --project="$GCP_PROJECT" \
  --region="$REGION" \
  --display_name="$DISPLAY_NAME" \
  "$HERE/greet_agent"

echo "Done. The resource name (projects/.../reasoningEngines/<id>) is printed above."
