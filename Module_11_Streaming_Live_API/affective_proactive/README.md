<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Affective and proactive dialog

## What this shows

Two optional behaviors of native-audio Live models, each switched on by one
`RunConfig` field. No other code changes. Both are supported on Gemini 2.5
Flash Live (`gemini-live-2.5-flash-native-audio` on Agent Platform (formerly
Vertex AI), `gemini-2.5-flash-native-audio-preview-12-2025` on the Gemini API)
and are not supported on Gemini 3.1 Flash Live. Leaving them set is the most
common failure when moving to 3.1. This is a reference page with snippets.

## Prerequisites

- The Live setup from `../minimal_live_agent/README.md` (Live model, location,
  browser with microphone access).

## Run it

The `adk web` voice session (the call button) does not turn these on: its
client sends only `modalities=AUDIO` to the dev server's `/run_live`
WebSocket. The
endpoint itself accepts both flags as query parameters, so a custom client of
`adk web` or `adk api_server` can enable them per session:

```
ws://localhost:8000/run_live?app_name=lab_voice_tutor&user_id=u1&session_id=<id>&modalities=AUDIO&enable_affective_dialog=true&proactive_audio=true
```

Create the session first with
`POST /apps/lab_voice_tutor/users/u1/sessions`. In your own Python server, set
the fields on the `RunConfig` you pass to `run_live()`, as below.

## What to look for

What each flag changes, and how to set it in Python.

### Affective dialog

The model reads tone in the user's voice (frustration, excitement, hesitation)
and adapts its delivery.

```python
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
    enable_affective_dialog=True,
)
```

### Proactive audio

The model decides when to respond: it can stay silent on input that is not
meant for it, or speak up without a direct question.

```python
from google.adk.agents.run_config import RunConfig
from google.genai import types

run_config = RunConfig(
    response_modalities=["AUDIO"],
    proactivity=types.ProactivityConfig(proactive_audio=True),
)
```

### Both together

```python
import os

from google.adk.agents import LlmAgent
from google.adk.agents.run_config import RunConfig
from google.genai import types

agent = LlmAgent(
    name="warm_tutor",
    model=os.getenv("LIVE_MODEL", "gemini-live-2.5-flash-native-audio"),
    instruction="You are a patient, warm tutor. Notice when the user struggles.",
)

run_config = RunConfig(
    response_modalities=["AUDIO"],
    enable_affective_dialog=True,
    proactivity=types.ProactivityConfig(proactive_audio=True),
)
```

## Trade-offs

Both behaviors are probabilistic, so responses become less predictable.

Leave them off for:

- Transactional voice apps (bookings, order lookups), where unprompted speech
  gets in the way.
- Regulated or high-stakes domains, where unsolicited statements are a risk.
- Debugging, where you want repeatable behavior.
- Short commands, where there is too little audio to read tone from.

They help most in tutoring and coaching, companion apps, and long support
calls where the user may go quiet.

## Further reading

- ADK docs, proactivity and affective dialog: https://google.github.io/adk-docs/live/configuration/#proactivity-and-affective-dialog
