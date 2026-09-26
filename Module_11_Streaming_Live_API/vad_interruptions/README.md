<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Voice activity detection and interruptions

## What this shows

How a live session decides when the user has started and stopped talking, and
what a client does when the user talks over the agent. Turn detection runs
inside the Live API, and you tune it through
`RunConfig.realtime_input_config`. This is a reference page with snippets.

With automatic voice activity detection (VAD), which is on by default:

- When the user starts speaking, the model stops talking and ADK yields an
  event with `interrupted=True`.
- When the user stops speaking, the model responds. No "end of turn" signal
  is needed from your code.

## Prerequisites

- The Live setup from `../minimal_live_agent/README.md` (Live model, location,
  browser with microphone access), to see the default behavior.

## Run it

The default VAD is what every `adk web` voice session uses, so you can
watch it with any Live agent in this module:

1. `cd Module_11_Streaming_Live_API`
2. `adk web` (on Agent Platform: `GOOGLE_CLOUD_LOCATION=us-central1 adk web`)
3. Select `minimal_live_agent`, click the call (phone) button in the message
   box and ask: "Tell me about the history of the Python language."
4. While it answers, say "Stop, that's enough."

`adk web` has no setting for `realtime_input_config`; the tuning below goes
into the `RunConfig` of a Python program that calls `run_live()`.

## What to look for

- The agent's audio stops within a moment of you speaking, and it answers the
  interruption instead of finishing the old sentence. The dev UI drops the
  audio it had queued when the `interrupted` event arrives.
- Pause for a second mid-sentence: with the default settings the model may
  take the pause as the end of your turn. The settings below change that.

## Tuning automatic VAD

```python
from google.adk.agents.run_config import RunConfig
from google.genai import types

run_config = RunConfig(
    response_modalities=["AUDIO"],
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            disabled=False,
            start_of_speech_sensitivity=types.StartSensitivity.START_SENSITIVITY_HIGH,
            end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_HIGH,
            prefix_padding_ms=200,     # audio kept from before speech was detected
            silence_duration_ms=800,   # silence needed before the turn counts as over
        )
    ),
)
```

| Setting | Higher / longer | Lower / shorter |
|---|---|---|
| `start_of_speech_sensitivity` | Reacts to quieter sound; faster interruptions, more false triggers | Needs clearer speech to start a turn |
| `end_of_speech_sensitivity` | Ends the turn sooner after silence | Waits longer before answering |
| `silence_duration_ms` | Lets users pause mid-sentence | Answers faster, may cut users off |

## Manual turn control

Disable automatic VAD when your app decides turn boundaries itself, for
example a push-to-talk button or a client-side VAD model:

```python
realtime_input_config=types.RealtimeInputConfig(
    automatic_activity_detection=types.AutomaticActivityDetection(disabled=True)
)
```

Then mark each turn on the queue:

```python
live_request_queue.send_activity_start()
# ... send_realtime() audio frames ...
live_request_queue.send_activity_end()
```

## Handling interruptions in the client

```python
async for event in runner.run_live(...):
    if event.interrupted:
        audio_player.stop()  # drop audio already queued for playback
```

Without this, the user hears the rest of the old answer on top of the new
one. The `adk web` client does this for you.

## Common errors

- The model cuts the user off mid-sentence: raise `silence_duration_ms`
  (1000 to 1500) or lower `end_of_speech_sensitivity`.
- The model is slow to answer: lower `silence_duration_ms` or raise
  `end_of_speech_sensitivity`.
- Background noise triggers the model: lower `start_of_speech_sensitivity`
  and add noise suppression on the client (`getUserMedia` supports
  `noiseSuppression: true`).

## Further reading

- ADK docs, voice activity detection: https://google.github.io/adk-docs/live/configuration/#voice-activity-detection-vad
