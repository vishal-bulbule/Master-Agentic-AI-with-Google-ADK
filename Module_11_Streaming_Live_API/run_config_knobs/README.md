<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# RunConfig for live sessions

## What this shows

`RunConfig` is passed to `runner.run_live()` and shapes one live session:
output modality, voice, transcription, reconnection and long-session
behavior. Two users of the same agent can run with different configs. This is
a reference page with snippets; every snippet was checked against google-adk
2.9.2 and google-genai 2.24.

```python
from google.adk.agents.run_config import RunConfig
from google.genai import types

run_config = RunConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Charon")
        )
    ),
    session_resumption=types.SessionResumptionConfig(),
)
```

## Prerequisites

- The Live setup from `../minimal_live_agent/README.md` (Live model, location,
  browser with microphone access), if you want to hear a change.

## Run it

This topic has no agent of its own. In `adk web`, the dev server builds the
`RunConfig` for each voice session itself, from query parameters on its
`/run_live` WebSocket: `modalities` (always `AUDIO` from the dev UI),
`proactive_audio`, `enable_affective_dialog`, `enable_session_resumption`,
`save_live_blob` and `explicit_vad_signal`. The dev UI sends only
`modalities`; the others are for custom clients of the same endpoint.

The one knob you can try in `adk web` without writing a client is the voice,
because it can be set on the model instead of the `RunConfig`:

1. In `../minimal_live_agent/agent.py`, replace `model=LIVE_MODEL` with:

   ```python
   from google.adk.models import Gemini
   from google.genai import types

   model=Gemini(
       model=LIVE_MODEL,
       speech_config=types.SpeechConfig(
           voice_config=types.VoiceConfig(
               prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Charon")
           )
       ),
   ),
   ```

2. `cd Module_11_Streaming_Live_API && adk web`, select `minimal_live_agent`,
   click the call (phone) button in the message box and talk. The voice has
   changed.

Everything else on this page goes into the `RunConfig` of a Python program
that calls `run_live()` (see "Using this from Python" in
`../minimal_live_agent/README.md`).

## What to look for

### Selecting the Live API: call `run_live()`

`runner.run_live()` is what opens the bidirectional Live API connection (the
`adk web` call (phone) button calls it through `/run_live`).
`RunConfig.streaming_mode` is only read by `run_async()`:

| `streaming_mode` | Effect on `run_async()` |
|---|---|
| `StreamingMode.NONE` (default) | One complete response per model call |
| `StreamingMode.SSE` | Partial chunks as the model generates them (see `token_streaming/`) |
| `StreamingMode.BIDI` | No effect in Python; `run_live()` never reads it |

Older samples set `streaming_mode=StreamingMode.BIDI` for live sessions. It
does nothing and can be removed.

### `response_modalities`

Current Live models produce audio only, so a live session uses
`["AUDIO"]` (ADK fills this in when unset). `["TEXT"]` fails against these
models. To get text out of a live session, read the transcription. `["TEXT"]`
is still valid on the `run_async()` path with standard Gemini models.

### `speech_config`: voice and language

```python
speech_config = types.SpeechConfig(
    voice_config=types.VoiceConfig(
        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Charon")
    ),
    language_code="en-US",
)
```

Prebuilt voices include Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, and
Zephyr. An unsupported voice fails when the connection opens. A voice set on
the agent's model (`Gemini(model=..., speech_config=...)`) wins over the one in
`RunConfig`.

### `input_audio_transcription` / `output_audio_transcription`

Both are on by default in ADK live sessions. Transcripts arrive on
`event.input_transcription` and `event.output_transcription` in fragments;
`.finished` marks the last fragment of a turn. Set a field to `None` to turn
that direction off.

```python
RunConfig(response_modalities=["AUDIO"], input_audio_transcription=None)
```

### `session_resumption`: survive connection drops

```python
session_resumption=types.SessionResumptionConfig()
```

Live API connections are recycled roughly every 10 minutes. With resumption
on, ADK caches the latest resumption handle and reconnects transparently, so
the conversation continues without replaying history.

### `context_window_compression`: sessions longer than the limits

```python
context_window_compression=types.ContextWindowCompressionConfig(
    trigger_tokens=100000,
    sliding_window=types.SlidingWindow(target_tokens=80000),
)
```

When the context reaches `trigger_tokens`, older turns are dropped down to
`target_tokens`. This lets a session run past the audio session duration
limit (15 minutes audio-only). The trade-off: the model loses precise recall of
early turns.

### Proactivity and affective dialog

Extra flags on the same `RunConfig`, supported on Gemini 2.5 Flash Live only.
See `affective_proactive/`.

## Typical configurations

Voice assistant with captions and reconnection:

```python
RunConfig(
    response_modalities=["AUDIO"],
    session_resumption=types.SessionResumptionConfig(),
)
```

Long-running monitoring agent:

```python
RunConfig(
    response_modalities=["AUDIO"],
    session_resumption=types.SessionResumptionConfig(),
    context_window_compression=types.ContextWindowCompressionConfig(
        trigger_tokens=100000,
        sliding_window=types.SlidingWindow(target_tokens=80000),
    ),
)
```

## Further reading

- ADK docs, live configuration: https://google.github.io/adk-docs/live/configuration/
- ADK docs, live sessions: https://google.github.io/adk-docs/live/sessions/
