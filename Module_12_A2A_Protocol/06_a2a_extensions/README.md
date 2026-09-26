<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 06: A2A extensions

## What this shows

The core A2A protocol covers tasks and their states, messages (text, file,
and data parts), agent cards, and standard auth schemes. Anything beyond that,
such as domain metadata, custom auth rules, or vendor-specific behavior, goes
in an extension. The `ticket_desk` agent here advertises the extension ADK
itself defines in its `agent.json` card. You call it over A2A twice, once
without and once with the extension activated, and compare the replies. A
custom tenant-id extension (card entry, server-side check, client headers)
is shown as a snippet at the end, because enforcing it needs your own server
code.

```
06_a2a_extensions/
  ticket_desk/
    __init__.py
    agent.py        root_agent with one tool, get_ticket
    agent.json      A2A card; capabilities.extensions lists the ADK extension
    .env.example
```

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)). The root
      `requirements.txt` installs `google-adk[a2a]`, which pulls in `a2a-sdk`.
- [ ] Credentials in a `.env`: copy `ticket_desk/.env.example` to
      `ticket_desk/.env` (or use the root `.env`). Either a Gemini API key or
      Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location
      `global`.
- [ ] Port 8081 free (stop the servers from topics 02 and 05). To use another
      port, change the `url` in `ticket_desk/agent.json` too.

## Run it

1. `cd Module_12_A2A_Protocol/06_a2a_extensions`
2. `adk api_server --a2a --port 8081`
3. In another terminal, read the extensions the card advertises:

   ```bash
   curl -s http://localhost:8081/a2a/ticket_desk/.well-known/agent-card.json
   ```

4. Call the agent without activating the extension:

   ```bash
   curl -s http://localhost:8081/a2a/ticket_desk \
     -H 'Content-Type: application/json' \
     -H 'A2A-Version: 1.0' \
     -d '{"jsonrpc": "2.0", "id": "1", "method": "SendMessage",
          "params": {"message": {"messageId": "m1", "role": "ROLE_USER",
                     "parts": [{"text": "What is the status of ticket T-100?"}]}}}'
   ```

5. Send the same request with the extension activated:

   ```bash
   curl -s http://localhost:8081/a2a/ticket_desk \
     -H 'Content-Type: application/json' \
     -H 'A2A-Version: 1.0' \
     -H 'A2A-Extensions: https://google.github.io/adk-docs/a2a/a2a-extension/' \
     -d '{"jsonrpc": "2.0", "id": "1", "method": "SendMessage",
          "params": {"message": {"messageId": "m1", "role": "ROLE_USER",
                     "parts": [{"text": "What is the status of ticket T-100?"}]}}}'
   ```

## What to look for

- Step 3: `capabilities.extensions` lists the ADK extension URI. `required`
  is missing from the served JSON: `false` is the protobuf default, and
  a2a-sdk 1.x omits default values when it serializes the card.
- Step 4 (legacy executor): the task is `TASK_STATE_COMPLETED`, `artifacts`
  holds only the answer text ("T-100 is open ... high priority ... network
  team"), and `history` repeats the user message, the `get_ticket`
  `function_call` and `function_response` data parts, and the answer again.
- Step 5 (ADK extension active): `history` holds only the user message,
  `artifacts` carries the `function_call`, the `function_response` and the
  answer, and the task `metadata` has a key named after the extension URI.
  That key is how the server tells the client it activated the extension.
- Both calls succeed: a client that ignores a `required: false` extension
  still gets an answer.

## How extensions work

An extension is identified by a URI. The server lists the extensions it
supports in its agent card:

```json
"capabilities": {
  "extensions": [
    {
      "uri": "https://google.github.io/adk-docs/a2a/a2a-extension/",
      "description": "Ability to use the new agent executor implementation",
      "required": false
    }
  ]
}
```

- `required: false`: clients that do not know the extension can still call
  the agent; they do not get the extra behavior.
- `required: true`: clients must activate the extension or the server rejects
  the request.

A client activates extensions by listing their URIs, comma-separated, in the
`A2A-Extensions` HTTP header (gRPC metadata for gRPC). Protocol 0.3 used
`X-A2A-Extensions`; a2a-sdk 1.x servers accept that name only on requests
that use the 0.3 protocol.

## The ADK extension

ADK defines `https://google.github.io/adk-docs/a2a/a2a-extension/`. When a
request activates it, ADK's `A2aAgentExecutor` uses its newer implementation,
which:

- does not duplicate the user message or the answer in the task history,
- does not turn the remote agent's output into "thought" parts,
- keeps the output of nested sub-agents instead of dropping it.

ADK servers honor the extension whether or not the card lists it; listing it
tells clients it is available. On the client, `RemoteA2aAgent` with
`use_legacy=False` sends the header for you:

```python
remote_agent = RemoteA2aAgent(
    name="ticket_desk",
    agent_card=f"http://localhost:8081/a2a/ticket_desk{AGENT_CARD_WELL_KNOWN_PATH}",
    use_legacy=False,
)
```

## A custom extension

A tenant-id extension shows the three pieces you write yourself: the card
entry, the server-side check, and the client headers. `adk api_server` does
not pass HTTP headers to your agent, so enforcing a custom extension needs
your own ASGI app (serve with `to_a2a(agent, agent_card=card)` from topic 02
and run the check in middleware). On the client, ADK attaches headers through
a request interceptor (`A2aRemoteAgentConfig(request_interceptors=[...])`).
Checked against a2a-sdk 1.1.5:

```python
from a2a.extensions.common import HTTP_EXTENSION_HEADER  # "A2A-Extensions"
from a2a.types import AgentCard, AgentExtension

TENANT_EXTENSION_URI = "https://example.com/a2a/ext/tenant-id/v1/"
TENANT_HEADER = "X-Tenant-Id"


def advertise_tenant_extension(card: AgentCard) -> AgentCard:
    """Lists the extension on the card once (serve it with to_a2a(agent, agent_card=card))."""
    if not any(e.uri == TENANT_EXTENSION_URI for e in card.capabilities.extensions):
        card.capabilities.extensions.append(AgentExtension(
            uri=TENANT_EXTENSION_URI,
            description=f"Every request carries the tenant id in {TENANT_HEADER}.",
            required=True,
        ))
    return card


def tenant_id_from(headers: dict[str, str]) -> str:
    """Server-side check: the client must activate the extension and send the id."""
    activated = {u.strip() for u in headers.get(HTTP_EXTENSION_HEADER, "").split(",")}
    if TENANT_EXTENSION_URI not in activated:
        raise PermissionError(f"Activate {TENANT_EXTENSION_URI} in {HTTP_EXTENSION_HEADER}.")
    if not headers.get(TENANT_HEADER):
        raise PermissionError(f"{TENANT_HEADER} header is missing.")
    return headers[TENANT_HEADER]


# Client side: the headers to send on every request.
client_headers = {HTTP_EXTENSION_HEADER: TENANT_EXTENSION_URI, TENANT_HEADER: "acme-corp"}
```

A request that does not list the URI in `A2A-Extensions` is rejected even
when it carries the tenant header: activation is explicit.

Typical reasons to write one:

| Use case | Why an extension |
|---|---|
| Org-specific auth rules (mTLS plus a signed JWT) | Beyond what the standard schemes express. |
| Domain metadata on every message (a tenant id) | The core spec has no field for it. |
| Capability gating (a PII-safe mode clients must accept) | `required: true` lets the server refuse clients that do not comply. |

## Conventions

1. Use a URL you control as the URI, never a bare name like `streaming-v2`.
2. Make the URI resolve to a page that documents the wire format.
3. Put the version in the path (`.../tenant-id/v1/`) so v2 is a new
   identifier rather than a breaking change.
4. Default to `required: false`. Require an extension only when the agent
   cannot run safely without it.

## Common errors

| Symptom | Cause |
|---|---|
| `VERSION_NOT_SUPPORTED` | A malformed `A2A-Version` header (for example two headers merged into one line). It must be exactly `1.0`. |
| No extension key in the task `metadata` | The `A2A-Extensions` value does not match the URI exactly, including the trailing `/`. |
| `404` on `/a2a/ticket_desk` | `--a2a` was not passed, or `agent.json` is missing or invalid. |

## Clean up

Stop the server with Ctrl+C. Sessions are stored under `ticket_desk/.adk/`;
delete that folder to start fresh.
