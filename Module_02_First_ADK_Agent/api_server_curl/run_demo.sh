#!/usr/bin/env bash
# Author: Vishal Bulbule
# Date: 2026-09-22

# Demo curl flow against `adk api_server`.
#
# Prereq: in another terminal, from Module_02_First_ADK_Agent/, run:
#   adk api_server
#
# This script:
#   1. Calls /list-apps to confirm the server sees the agents.
#   2. Creates a session for the weather_jokes_agent.
#   3. Sends two messages and prints the SSE event stream from each.

set -euo pipefail

HOST="${ADK_HOST:-http://localhost:8000}"
APP="weather_jokes_agent"
USER_ID="u1"
SESSION_ID="s_$(date +%s)"   # unique per run, avoids "session already exists"

echo "=== 1. Discover agents (GET /list-apps) ==="
curl -sS "${HOST}/list-apps"
echo -e "\n"

echo "=== 2. Create session ${SESSION_ID} for app ${APP} ==="
curl -sS -X POST \
  "${HOST}/apps/${APP}/users/${USER_ID}/sessions" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"${SESSION_ID}\"}"
echo -e "\n"

send_message() {
  local text="$1"
  echo "=== Sending: ${text} ==="
  curl -sS -N -X POST "${HOST}/run_sse" \
    -H "Content-Type: application/json" \
    -d "{
      \"appName\": \"${APP}\",
      \"userId\": \"${USER_ID}\",
      \"sessionId\": \"${SESSION_ID}\",
      \"newMessage\": {
        \"role\": \"user\",
        \"parts\": [{\"text\": \"${text}\"}]
      },
      \"streaming\": false
    }"
  echo -e "\n"
}

echo "=== 3. Ask about the weather (should call get_weather) ==="
send_message "What is the weather in Tokyo?"

echo "=== 4. Ask for a joke (should call tell_joke) ==="
send_message "Tell me a joke."

echo "=== 5. Inspect final session state ==="
curl -sS "${HOST}/apps/${APP}/users/${USER_ID}/sessions/${SESSION_ID}"
echo -e "\n=== Done ==="
