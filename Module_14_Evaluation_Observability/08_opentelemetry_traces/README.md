<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 08 - OpenTelemetry Traces

## What this shows

ADK creates OpenTelemetry spans for every agent run, model call, and tool call, following
the [GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md).
The agent needs no tracing code: `traced_agent/agent.py` is a plain time-lookup agent.
Where the spans go is a flag on the server: the `adk web` dev UI keeps them in memory
and shows them in its Traces view (the toggle next to Events in the main panel), and
`--trace_to_cloud` also exports them to Google Cloud Trace.

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)).
- Credentials: copy `traced_agent/.env.example` to `traced_agent/.env` and fill it in.
  Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on
  location `global`.
- Only for Cloud Trace export (optional):
  - `opentelemetry-exporter-gcp-trace` (in the root `requirements.txt`).
  - A Google Cloud project with the Cloud Trace API enabled:
    `gcloud services enable cloudtrace.googleapis.com --project=your-project-id`
  - `GOOGLE_CLOUD_PROJECT` exported in your shell (`export GOOGLE_CLOUD_PROJECT=your-project-id`)
    or set in a `.env` in this folder or above. The exporter is set up at server start and
    does not read `traced_agent/.env`.
  - Application default credentials: `gcloud auth application-default login`, with
    `roles/cloudtrace.agent` on the project for that identity:

    ```bash
    gcloud projects add-iam-policy-binding your-project-id \
      --member="user:you@example.com" --role="roles/cloudtrace.agent"
    ```

## Run it

1. `cd Module_14_Evaluation_Observability/08_opentelemetry_traces`
2. `adk web`
   (to also export to Cloud Trace: `adk web --trace_to_cloud`)
3. Open http://localhost:8000 and select `traced_agent` in the agent dropdown.
4. Send: "What time is it in Tokyo?", then "What about London?"
5. Click **Traces** (next to **Events**, top of the main panel).

With `--trace_to_cloud`, open Trace Explorer in the Cloud Console
(https://console.cloud.google.com/traces/list) for that project. Traces can take up to a
minute to appear.

## What to look for

The Traces view shows one tree per turn. A tested run of the two prompts:

```
invocation                               4095.8 ms
  invoke_agent traced_agent              4090.5 ms
    call_llm                             2062.9 ms
      generate_content gemini-3.5-flash  2054.4 ms  input_tokens=182 output_tokens=72
      execute_tool get_time                 1.9 ms
    call_llm                             1235.4 ms
      generate_content gemini-3.5-flash  1232.1 ms  input_tokens=306 output_tokens=67
invocation (second turn)                 2952.3 ms  input_tokens 377, then 488
```

- One turn is two model calls: one that decides to call `get_time`, one that writes the
  answer. The tool itself takes about 2 ms; the time is in the model calls.
- `gen_ai.usage.input_tokens` grows from turn to turn because the session history is
  sent with every call. That is where long conversations get expensive.
- Click a span to see its attributes: the model name, the tool name and arguments, and
  the token counts.

## Other ways to export

- `adk web --otel_to_cloud` (and `adk deploy cloud_run --otel_to_cloud`) sends traces,
  metrics, and logs over OTLP to the Google Cloud Telemetry API
  (`telemetry.googleapis.com`) instead of using the Cloud Trace exporter. It is marked
  experimental in ADK 2.9.2 and needs that API enabled
  (`gcloud services enable telemetry.googleapis.com`).
- Set `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` before starting `adk web` to send spans to
  any OTLP collector (Jaeger, Grafana Tempo, Langfuse, Phoenix). ADK reads the standard
  OTel environment variables at startup.

## Using this from Python

When you run the agent from your own code instead of `adk web`, install a global
TracerProvider once, before the Runner is created, and wrap your request handler in
your own span; ADK's spans nest under it:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("my-service")

with tracer.start_as_current_span("handle_user_turn"):
    async for event in runner.run_async(user_id=..., session_id=..., new_message=...):
        ...
```

## Common errors

| Error | Cause |
|---|---|
| Traces view is empty | The turn failed before a model call, or you opened a session from before the server restarted (spans are kept in memory). |
| `ModuleNotFoundError: opentelemetry.exporter.cloud_trace` | `--trace_to_cloud` without `opentelemetry-exporter-gcp-trace` installed. |
| `GOOGLE_CLOUD_PROJECT environment variable is not set. Tracing will not be enabled.` | `--trace_to_cloud` with no project in the shell environment. Export `GOOGLE_CLOUD_PROJECT` before `adk web`. |
| No traces in Cloud Trace | Missing `roles/cloudtrace.agent` for the credentials, or the Cloud Trace API is not enabled. |

## Clean up

Stop `adk web` with Ctrl+C and delete `traced_agent/.adk/` to drop local sessions.
Traces in Cloud Trace expire on their own (30 days); there is nothing to delete.
