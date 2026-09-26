<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 08: OpenAPI Tools

## What this shows

With an OpenAPI 3.x spec you do not need to hand-write tools.
`OpenAPIToolset` parses the spec and generates one tool per operation:

| In the spec | Becomes |
|---|---|
| `operationId` | Tool name |
| `summary` / `description` | Tool description (sent to the model) |
| `parameters` (path, query, header) | Tool parameters (names converted to snake_case, so `petId` becomes `pet_id`) |
| `requestBody` | Tool parameters (body fields) |

`petstore.yaml` defines three operations: `list_pets`, `get_pet` and
`create_pet`. The server is `httpbin.org`, which echoes back whatever
request it receives, so there is no real backend or secret.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`agent/.env.example`](agent/.env.example):
      `GOOGLE_API_KEY`, or Agent Platform (formerly Vertex AI) with
      `GOOGLE_CLOUD_LOCATION=global` (`gemini-3.5-flash` is served from
      `global`).
- [ ] Outbound HTTPS to `httpbin.org`.

## Run it

1. `cd Module_04_Custom_Tools/08_openapi_tool`
2. `adk web`
3. Open http://localhost:8000 and pick `agent` in the app dropdown in the top bar.
4. Send: "List all pets."

Terminal alternative: `adk run agent`.

## Try it

- "List all pets."
- "Get pet 42."
- "Add a new pet called Mochi, a cat."

## What to look for

- Events view: each prompt produces a call to the matching generated tool.
- The tool result is httpbin's echo: for `create_pet`, the `data` field
  holds the JSON body `{"name":"Mochi","species":"cat"}` that ADK built from
  the spec's `requestBody` schema.

## When to use OpenAPI tools

- Internal APIs you control and already maintain a spec for.
- Third-party APIs with clean specs.
- Anywhere hand-writing many near-identical wrappers would be repetitive.

The generated tools are only as good as the spec: a clear `operationId` and
`description` matter as much as a clear function name and docstring. The
trade-off: you give up per-tool control over error handling and response
shaping unless you post-process. When the API requires auth, pass
`auth_scheme` and `auth_credential` to `OpenAPIToolset(...)`; see
`09_tool_auth/`.
