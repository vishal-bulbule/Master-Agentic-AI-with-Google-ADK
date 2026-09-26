#!/usr/bin/env bash
# Author: Vishal Bulbule
# Date: 2026-09-22

# Lab 15: check the deployed service rejects anonymous calls and answers an
# authenticated one.
#
# Run:
#   URL=https://greet-agent-prod-<hash>.us-central1.run.app bash verify.sh

set -euo pipefail

: "${URL:?Set URL to the deployed Cloud Run service URL}"
APP_NAME="${APP_NAME:-greet_agent}"
USER_ID="${USER_ID:-u1}"
SESSION_ID="${SESSION_ID:-s-$(date +%s)}"

echo "==> Anonymous request (expect 401 or 403)"
CODE=$(curl -s -o /dev/null -w "%{http_code}" "${URL}/list-apps")
echo "    HTTP $CODE"
case "$CODE" in
  401|403) ;;
  *) echo "Service answered without a token; check --no-allow-unauthenticated." >&2; exit 1 ;;
esac

echo "==> Getting an identity token"
TOKEN=$(gcloud auth print-identity-token)
[ -n "$TOKEN" ] || { echo "Empty token. Run 'gcloud auth login' first." >&2; exit 1; }

echo "==> Creating session $SESSION_ID"
curl -fsS -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "${URL}/apps/${APP_NAME}/users/${USER_ID}/sessions" \
  -d "{\"session_id\": \"${SESSION_ID}\"}"
echo

echo "==> Calling /run_sse"
curl -fsS -N -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "${URL}/run_sse" \
  -d "$(cat <<JSON
{
  "app_name": "${APP_NAME}",
  "user_id": "${USER_ID}",
  "session_id": "${SESSION_ID}",
  "new_message": {"role": "user", "parts": [{"text": "Please greet Priya."}]},
  "streaming": false
}
JSON
)"
echo
echo "==> Expect an event with the text 'Hello, Priya!' above."
