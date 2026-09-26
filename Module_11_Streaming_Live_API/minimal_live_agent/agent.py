# Author: Vishal Bulbule
# Date: 2026-09-22

"""Minimal Live API agent.

The agent is an ordinary LlmAgent. What makes it live is how it is run: the
adk web call (phone) button opens the /run_live WebSocket, and the server calls
runner.run_live() with a LiveRequestQueue. The one hard requirement here is a
model that supports the Live API.

The model ID differs by backend, so it comes from the LIVE_MODEL environment
variable. The default is the Agent Platform ID; on the Gemini API (AI Studio)
set LIVE_MODEL=gemini-2.5-flash-native-audio-preview-12-2025.
"""

import os

from google.adk.agents import LlmAgent

LIVE_MODEL = os.getenv("LIVE_MODEL", "gemini-live-2.5-flash-native-audio")

root_agent = LlmAgent(
    name="minimal_live_agent",
    model=LIVE_MODEL,
    instruction=(
        "You are a friendly voice assistant. Keep replies to one or two short "
        "sentences and speak naturally."
    ),
)
