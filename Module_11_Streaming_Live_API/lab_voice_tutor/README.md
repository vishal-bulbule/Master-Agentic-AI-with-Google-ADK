<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Lab: voice tutor for Python decorators

## What this shows

A complete voice agent: microphone in, speech out, a tool the agent calls
mid-conversation, and interruption at any time. `agent.py` is an `LlmAgent`
on a Live model, restricted by its instruction to Python decorators, with one
ordinary (non-streaming) tool, `lookup_definition(term)`. When the model calls
it during a spoken turn, ADK runs the function, sends the result back over the
same live connection, and the model keeps talking from it. The tool has
definitions for `closure`, `decorator`, `generator`, `context manager` and
`list comprehension`, and returns `status: "not_found"` for anything else.

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)).
- Chrome or Edge with microphone access, and speakers or headphones.
- A Live model: copy `.env.example` to `.env` in this folder and set
  `LIVE_MODEL` and the location for your backend. Gemini API:
  `gemini-2.5-flash-native-audio-preview-12-2025`. Agent Platform (formerly
  Vertex AI): `gemini-live-2.5-flash-native-audio` on a region such as
  `us-central1` (not `global`), with the model allowed by your organization
  policy. Details in `../minimal_live_agent/README.md`.

## Run it

1. `cd Module_11_Streaming_Live_API`
2. `adk web` (on Agent Platform: `GOOGLE_CLOUD_LOCATION=us-central1 adk web`)
3. Open http://localhost:8000 and select `lab_voice_tutor`.
4. Click the call (phone) button in the message box, allow microphone
   access, and say: "Hi, I'm new to decorators. Where should I start?"

## Try it

- "Hi, I'm new to decorators. Where should I start?"
- "What is a closure?" (should call the tool)
- Start speaking while the tutor is mid-sentence (interruption).
- "Show me a decorator that times a function."
- "What's the weather today?" (the tutor should steer back to decorators)

## What to look for

| Behavior | Where it shows |
|---|---|
| Voice round trip | You hear the tutor; both sides appear as transcripts in the chat |
| Tool call | A `lookup_definition` call with `{"term": "closure"}` and its response in the session's events; the spoken answer starts with the returned definition |
| Interruption | The tutor's audio stops as soon as you speak |
| Topic discipline | Off-topic questions are redirected to decorators |

## Ideas to extend

- Add a `quiz(term)` tool that asks the learner a follow-up question.
- Try affective dialog (see `../affective_proactive/`). The `adk web`
  voice session has no switch for it, but the same `/run_live` endpoint
  accepts `enable_affective_dialog=true` from a custom client.
- Sessions already persist: `adk web` stores them in `lab_voice_tutor/.adk/`,
  so the session dropdown keeps earlier tutoring sessions after a restart.

## Common errors

| Symptom | Cause |
|---|---|
| `1008 ... was not found` or `1007 ... Organization Policy` in the terminal | Live model or location problem; see `../minimal_live_agent/README.md` |
| An error when typing in the chat box | Live models only answer in a voice session; use the call (phone) button |
| The tutor answers "what is X" without calling the tool | The model skipped it; ask again with the exact term, for example "What is a generator?" |
