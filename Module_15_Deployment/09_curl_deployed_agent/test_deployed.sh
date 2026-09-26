#!/usr/bin/env bash
# Author: Vishal Bulbule
# Date: 2026-09-22

# Call a deployed ADK agent over HTTP: create a session, then send one message.
#
# Works for any server that runs the ADK API (`adk deploy cloud_run`,
# `adk api_server`, or a custom image built on get_fast_api_app).
#
# Auth: by default the script sends a Google identity token, which a Cloud Run
# service deployed with --no-allow-unauthenticated requires. Set NO_AUTH=1 for
# a public service or a local `adk api_server`.
#
# Required:
#   URL        base URL of the service, e.g. https://greet-agent-<hash>.us-central1.run.app
#   APP_NAME   agent folder name, e.g. greet_agent
#
# Run:
#   export URL=https://greet-agent-<hash>.us-central1.run.app
#   export APP_NAME=greet_agent
#   bash test_deployed.sh "Priya"

set -euo pipefail

: "${URL:?Set URL to the service URL}"
: "${APP_NAME:?Set APP_NAME to the agent folder name, e.g. greet_agent}"

NAME="${1:-Priya}"
USER_ID="${USER_ID:-u1}"
SESSION_ID="${SESSION_ID:-s-$(date +%s)}"

# ${AUTH_HEADER[@]+...} below keeps an empty array safe under `set -u` in bash 3.2 (macOS).
AUTH_HEADER=()
if [ -z "${NO_AUTH:-}" ]; then
  echo "[1/3] Getting an identity token for the current gcloud account"
  TOKEN=$(gcloud auth print-identity-token)
  [ -n "$TOKEN" ] || { echo "Empty token. Run 'gcloud auth login' first." >&2; exit 1; }
  AUTH_HEADER=(-H "Authorization: Bearer $TOKEN")
else
  echo "[1/3] NO_AUTH set, sending requests without a token"
fi

echo "[2/3] Creating session $SESSION_ID for user $USER_ID"
curl -fsS -X POST ${AUTH_HEADER[@]+"${AUTH_HEADER[@]}"} \
  -H "Content-Type: application/json" \
  "${URL}/apps/${APP_NAME}/users/${USER_ID}/sessions" \
  -d "{\"session_id\": \"${SESSION_ID}\"}"
echo

echo "[3/3] Sending a message to /run_sse"
# -N disables curl's buffering so server-sent events print as they arrive.
curl -fsS -N -X POST ${AUTH_HEADER[@]+"${AUTH_HEADER[@]}"} \
  -H "Content-Type: application/json" \
  "${URL}/run_sse" \
  -d "$(cat <<JSON
{
  "app_name": "${APP_NAME}",
  "user_id": "${USER_ID}",
  "session_id": "${SESSION_ID}",
  "new_message": {"role": "user", "parts": [{"text": "Please greet ${NAME}."}]},
  "streaming": false
}
JSON
)"
echo
