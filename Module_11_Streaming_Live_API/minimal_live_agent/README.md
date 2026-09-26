<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Minimal Live agent

## What this shows

The smallest Live API agent: an ordinary `LlmAgent` on a Live model, spoken
to through the call (phone) button in the `adk web` message box. Nothing in
`agent.py` is live-specific except the model. What makes a session live is
how it is run: the call button opens the dev server's `/run_live` WebSocket,
and the server calls `runner.run_live()` with a `LiveRequestQueue`, streaming
16 kHz PCM from your microphone in and 24 kHz PCM audio plus transcripts out. No
flag is needed on `adk web`; any agent whose model supports the Live API gets
a voice session.

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)).
- Chrome or Edge with microphone access, and speakers or headphones.
- A Live model your credentials can use. Copy `.env.example` to `.env` in this
  folder and pick one backend:

  | Backend | `LIVE_MODEL` | Location |
  |---|---|---|
  | Gemini API (AI Studio) | `gemini-2.5-flash-native-audio-preview-12-2025` | not used |
  | Agent Platform (formerly Vertex AI) | `gemini-live-2.5-flash-native-audio` (the default) | a region such as `us-central1`; `global` does not serve Live models |

- Agent Platform only: `gcloud auth application-default login`, the Agent
  Platform API enabled (`gcloud services enable aiplatform.googleapis.com`),
  and the Live model allowed by your organization's
  `constraints/vertexai.allowedGenAIModels` policy.
- macOS with python.org Python: `export SSL_CERT_FILE=$(python -m certifi)` in
  the shell you start `adk web` from (the ADK Live quickstart asks for this).

## Run it

1. `cd Module_11_Streaming_Live_API`
2. `adk web`
   On Agent Platform, if other agents in this folder use `global`, start it as
   `GOOGLE_CLOUD_LOCATION=us-central1 adk web`. A variable set in the shell
   wins over every `.env` file, and the whole server shares one environment.
3. Open http://localhost:8000 and select `minimal_live_agent`.
4. Click the call (phone) button in the message box, allow microphone access
   when the browser asks, and say: "Hello, can you hear me?"

`adk run` does not work for this agent: it sends text through `run_async()`,
and Live models do not answer that way.

## Try it

- "Hello, can you hear me?" then "Tell me a one-line joke."
- Start talking while the agent is answering. It stops mid-sentence; that is
  the Live API's server-side voice activity detection (see
  `../vad_interruptions/`).

## What to look for

- The chat shows your words and the agent's as transcripts. Live models reply
  in audio only; the text is the input and output transcription, which ADK
  turns on by default for live sessions.
- Every event the server sends is JSON on the `/run_live` WebSocket. In the
  browser's developer tools (Network, WS, Messages) you can watch
  transcription fragments, `turnComplete` at the end of each answer, and
  `interrupted` when you talk over the agent.
- The terminal running `adk web` logs the Live connection, including any error
  from the Live API.

## Using this from Python

What the dev server does per voice session, reduced to its core. A
`LiveRequestQueue` carries input in; `run_live()` yields events out; closing
the queue ends the session.

```python
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.runners import InMemoryRunner
from google.genai import types

runner = InMemoryRunner(agent=root_agent, app_name="minimal_live_agent")
session = await runner.session_service.create_session(
    app_name="minimal_live_agent", user_id="u1"
)
queue = LiveRequestQueue()
queue.send_realtime(types.Blob(mime_type="audio/pcm;rate=16000", data=pcm_bytes))

async for event in runner.run_live(
    session=session,
    live_request_queue=queue,
    run_config=RunConfig(response_modalities=["AUDIO"]),
):
    if event.output_transcription and event.output_transcription.text:
        print(event.output_transcription.text, end="")
    if event.turn_complete:
        queue.close()
```

Send and receive run concurrently in a real client (one task feeds the queue
while another reads events). `send_content()` sends a text turn instead of
audio. The dev server's `/run_live` endpoint accepts the same JSON
(`LiveRequest` in, `Event` out) from any WebSocket client, so a custom UI can
talk to `adk web` or `adk api_server` without its own server code.

## Common errors

| Symptom | Cause |
|---|---|
| `1008 ... Publisher model ... was not found` in the terminal | Wrong model ID for the backend, a retired model (`gemini-2.0-flash-live-001`), or `GOOGLE_CLOUD_LOCATION=global` |
| `1007 ... Organization Policy constraint constraints/vertexai.allowedGenAIModels violated` | Your organization does not allow this model. Ask an admin to allow it, or use the Gemini API |
| An error when typing in the chat box | The text box runs a normal `run_async()` turn, which Live models do not support. Use the call (phone) button |
| The call button does nothing | The browser blocked microphone access for `localhost`; allow it in the site settings |
| `SSL: CERTIFICATE_VERIFY_FAILED` when the session starts (macOS) | Set `SSL_CERT_FILE` as in Prerequisites |
