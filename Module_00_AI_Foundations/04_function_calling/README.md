<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Function calling

## What this shows

The loop an agent runs, done by hand and then by the SDK:

- `function_calling.py`: automatic function calling is off, so every step is
  visible. The model returns a `function_call`, your code runs the function,
  sends a `function_response` back, and the model writes the answer.
- `function_calling_gcs.py`: a plain Python function passed in `tools`; the
  SDK runs the whole loop against a real, read-only Cloud Storage call.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and `pip install -r requirements.txt`.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`,
      `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).
- [ ] For `function_calling_gcs.py` only: a Google Cloud project with the
      Cloud Storage API enabled, `GOOGLE_CLOUD_PROJECT` set in `.env`,
      Application Default Credentials
      (`gcloud auth application-default login`), and a role that includes
      `storage.buckets.list` on the project (for example Viewer,
      `roles/viewer`). This is needed even if you use a Gemini API key for
      the model.

## Run it

1. `cd Module_00_AI_Foundations/04_function_calling`
2. `python function_calling.py`
3. `python function_calling_gcs.py`

## What to look for

- `function_calling.py` prints the call the model requested
  (`get_weather({'city': 'Mumbai'})`), what the tool returned, and the final
  answer: four steps, two model calls.
- The script appends the model's own content to the history instead of a
  rebuilt copy. That keeps the thought signature Gemini 3.x requires on
  multi-turn function calling.
- `function_calling_gcs.py` prints the answer, then the `list_buckets` call
  and result the SDK exchanged for you, read from the chat history.
