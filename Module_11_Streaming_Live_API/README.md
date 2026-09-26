<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 11: Streaming and the Live API

ADK supports two kinds of streaming, on different model families and different
runner methods. Every agent in this module runs in `adk web`.

| Kind | What streams | Runner method | Models | In `adk web` |
|---|---|---|---|---|
| Token streaming | Model text, in chunks | `run_async()` with `StreamingMode.SSE` | Standard Gemini (`gemini-3.5-flash`) | More options (vertical dots, top right) > **Streaming** (`/run_sse`) |
| Live API (bidirectional) | Audio (and video) both ways, interruptible | `run_live()` with a `LiveRequestQueue` | Live models only | The call (phone) button in the message box (`/run_live` WebSocket) |

## Topics

Work through them in this order:

| # | Folder | What it shows |
|---|---|---|
| 1 | `token_streaming/` | Text chunks from `run_async()` with `StreamingMode.SSE` |
| 2 | `minimal_live_agent/` | The smallest Live agent, talked to from the `adk web` call (phone) button |
| 3 | `run_config_knobs/` | `RunConfig` fields for live sessions: modality, voice, transcription, resumption, compression |
| 4 | `streaming_tool/` | An `AsyncGenerator` tool the agent reacts to while it runs |
| 5 | `vad_interruptions/` | Voice activity detection settings and handling `interrupted` events |
| 6 | `affective_proactive/` | Affective dialog and proactive audio flags |
| Lab | `lab_voice_tutor/` | Voice tutor for Python decorators with a tool called mid-conversation |

Topics 3, 5 and 6 are reference pages with snippets; they have no agent of
their own.

## Before you start

- The repository setup: [SETUP.md](../SETUP.md).
- Chrome or Edge with microphone access, and speakers or headphones, for
  topics 2 to 6 and the lab.
- A `.env` in each agent folder, copied from its `.env.example`.
- A Live model your credentials can use (table below). On Agent Platform
  (formerly Vertex AI): `gcloud auth application-default login`, the Agent
  Platform API enabled, and the Live model allowed by your organization's
  `constraints/vertexai.allowedGenAIModels` policy.
- macOS with python.org Python: `export SSL_CERT_FILE=$(python -m certifi)`
  before starting `adk web` for voice sessions.

## Live models

The Live agents read the model ID from `LIVE_MODEL`, because the ID differs by
backend:

| Backend | `LIVE_MODEL` | `GOOGLE_CLOUD_LOCATION` |
|---|---|---|
| Gemini API (AI Studio) | `gemini-2.5-flash-native-audio-preview-12-2025` | not used |
| Agent Platform | `gemini-live-2.5-flash-native-audio` (default) | A region such as `us-central1`; `global` is not supported for Live models |

`token_streaming/` uses `gemini-3.5-flash`, which on Agent Platform is served
only from `global`. `adk web` shares one environment across all the agents it
loads, so on Agent Platform run the two groups separately:

```bash
cd Module_11_Streaming_Live_API
adk web                                        # token_streaming, location from .env (global)
GOOGLE_CLOUD_LOCATION=us-central1 adk web      # the Live agents; the shell value wins over every .env
```

`gemini-2.0-flash-live-001`, used by older samples, is retired.

## How `adk web` runs a Live agent

No flag is needed. When you click the call (phone) button in the message box
and allow microphone access, the dev UI opens a WebSocket to
`/run_live?app_name=...&user_id=...&session_id=...&modalities=AUDIO`.
The server builds a `RunConfig(response_modalities=["AUDIO"])`, creates a
`LiveRequestQueue`, and calls `runner.run_live()`. Microphone audio goes in as
16 kHz PCM; audio replies (24 kHz PCM) and transcripts come back as JSON
events, and playback stops when an `interrupted` event arrives. The text box
does not work with Live models: it runs an ordinary `run_async()` turn.
`adk api_server` serves the same `/run_live` endpoint without the UI, which is
what a custom client connects to.

## Choosing between them

- Text in, text out, and you want the answer to appear as it is written:
  token streaming.
- Voice in, voice out, with interruptions: the Live API.
- A tool that reports progress or watches something while the conversation
  continues: a streaming tool, which needs the Live API.

## Further reading

- ADK docs, live agents: https://google.github.io/adk-docs/live/
- ADK docs, building a custom live server: https://google.github.io/adk-docs/live/custom-server/
- bidi-demo sample: https://github.com/google/adk-samples/tree/main/python/agents/bidi-demo
