<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Module 0: AI Foundations (no framework)

Every script here uses the raw `google-genai` SDK, with no ADK. The goal is to
see what sits underneath an agent: a model call, its configuration, tool
calling, token accounting and MCP. Later modules hand each of these to ADK.

## Topics

Work through them in order.

| Folder | What it shows |
|---|---|
| `01_genai_basic_call/` | One model call and the full response object; `GenerateContentConfig` settings one by one; Flash vs Pro latency; Google Search grounding |
| `02_streaming/` | Streaming a response chunk by chunk |
| `03_multimodal/` | Image and text in the same request |
| `04_function_calling/` | The function-calling loop by hand, then the SDK running it automatically against Cloud Storage |
| `05_token_counting/` | Counting tokens and projecting cost |
| `06_prompt_engineering/` | A vague prompt vs one with role, task, constraints and an example |
| `07_temperature_demo/` | Output variance across temperatures, and why Gemini 3.x should stay at the default |
| `08_model_comparison/` | Same prompt on Flash and Pro: latency and token use |
| `09_mcp_grounding/` | Calling an MCP server with the `mcp` SDK directly |
| `10_same_call_with_adk/` | The topic 04 weather task as an ADK agent: same tool, no handwritten loop |
| `lab_doc_qa/` | Lab: a doc-grounded Q&A CLI that combines streaming, grounding and cost reporting |

## Before you start

- Repository setup from [SETUP.md](../SETUP.md): virtual environment,
  `pip install -r requirements.txt`, and a `.env` at the repository root.
  Every script calls `load_dotenv()`, which finds the nearest `.env` walking
  up from the script's folder. Each topic folder also has a `.env.example`
  listing the variables its scripts need.
- Gemini credentials. `genai.Client()` reads them from the environment:
  `GOOGLE_API_KEY` for the Gemini API, or `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`,
  `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION=global` for Agent
  Platform (formerly Vertex AI).
- `01_genai_basic_call` and `08_model_comparison`: access to `gemini-2.5-pro`
  for the Pro comparison (the scripts skip it if blocked).
- `04_function_calling/function_calling_gcs.py`: a Google Cloud project,
  Application Default Credentials (`gcloud auth application-default login`)
  and permission to list Cloud Storage buckets.
- `09_mcp_grounding`: Node.js with `npx`.

These are plain Python scripts, not ADK agents: run each one with `python`
from its own folder. Each topic folder has a README with the exact commands.

## Run any topic

```bash
cd Module_00_AI_Foundations/01_genai_basic_call
python basic_call.py
```

## Common errors

| Symptom | Cause |
|---|---|
| `ValueError: Missing key inputs argument!` | No `.env` found and no credentials exported. Create the root `.env` from `.env.example`. |
| `404 NOT_FOUND` for `gemini-3.5-flash` on Agent Platform | `GOOGLE_CLOUD_LOCATION` is a region such as `us-central1`. Set it to `global`. |
| `FAILED_PRECONDITION` or `PERMISSION_DENIED` for `gemini-2.5-pro` | The model is not enabled for your project, for example by an organization policy. The comparison scripts skip it and continue. |
| Log line `Direct use of automatic function calling (AFC) in Models.generate_content is not recommended` | Emitted once per process by the SDK on the first `generate_content` call, even without tools. It is harmless here. |
| `npx: command not found` in `09_mcp_grounding` | Install Node.js (see SETUP.md). |
