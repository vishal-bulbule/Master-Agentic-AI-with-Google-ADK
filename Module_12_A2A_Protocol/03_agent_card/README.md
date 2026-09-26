<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 03: Agent cards

## What this shows

An agent card is a JSON document that describes an A2A agent: its name,
version, skills, where to send requests, and how to authenticate. Clients
fetch the card first and use it to decide whether and how to call the agent.
It is the contract between the two sides. This topic explains the fields,
where the card is served, and validates a hand-written card against the
a2a-sdk schema.

## Prerequisites

- The repository setup ([SETUP.md](../../SETUP.md)). No credentials are needed
  to validate the card; inspecting a live card needs the topic 02 server.

## Run it

Validate the sample card. `ParseDict` is strict and rejects unknown fields, so
a 0.x card fails here:

1. `cd Module_12_A2A_Protocol/03_agent_card`
2. Run:

   ```bash
   python -c "import json; from google.protobuf.json_format import ParseDict; from a2a.types import AgentCard; print(ParseDict(json.load(open('sample_agent_card.json')), AgentCard()).name)"
   ```

   It prints `product_catalog`.

Inspect a live card:

1. `cd Module_12_A2A_Protocol/02_expose_agent`
2. `adk api_server --a2a --port 8081`
3. In another terminal:

   ```bash
   curl -s http://localhost:8081/a2a/product_catalog/.well-known/agent-card.json
   ```

## What to look for

- The live card is `02_expose_agent/product_catalog/agent.json`, served as
  written. `adk api_server --a2a` does not generate or rewrite it.
- The sample card here adds the optional fields: a provider, the ADK
  extension, and an API-key scheme. It declares the scheme but does not
  require it; to require it, add:

  ```json
  "securityRequirements": [{"schemes": {"api_key": {"list": []}}}]
  ```

## Where the card lives

| Server | Card URL |
|---|---|
| `adk api_server --a2a` / `adk web --a2a` | `http://<host>:<port>/a2a/<app_name>/.well-known/agent-card.json` |
| Your own app with `to_a2a(agent)` | `http://<host>:<port>/.well-known/agent-card.json` |

a2a-sdk 1.x serves the card at `.well-known/agent-card.json`. Older examples
use `/.well-known/agent.json`, which now returns 404. In code, use the
`AGENT_CARD_WELL_KNOWN_PATH` constant from
`google.adk.agents.remote_a2a_agent`.

The ADK CLI serves only agent folders that contain a hand-written `agent.json`
card. `to_a2a(root_agent)` in your own ASGI app takes the other route: it
builds the card from the agent (name, description, one `model` skill, one
skill per tool), or takes yours with `agent_card="sample_agent_card.json"`.

## Card fields (A2A protocol 1.0)

The card is a protobuf message (`a2a.types.AgentCard`); on the wire it is
JSON with camelCase field names.

| Field | Meaning |
|---|---|
| `name`, `description` | Identify the agent. A parent `LlmAgent` reads the description when deciding whether to delegate. |
| `version` | Version of the agent's contract, chosen by the owner. |
| `supportedInterfaces[]` | Where to send requests: `url`, `protocolBinding` (`JSONRPC`, `HTTP+JSON`, `GRPC`), and `protocolVersion`. Replaces the 0.x top-level `url`, `preferredTransport`, and `protocolVersion`. |
| `provider` | Organization and URL of the owner. |
| `capabilities` | `streaming`, `pushNotifications`, `extendedAgentCard`, and `extensions[]`. `extendedAgentCard` replaces 0.x `supportsAuthenticatedExtendedCard`. |
| `defaultInputModes`, `defaultOutputModes` | Media types the agent accepts and returns. |
| `skills[]` | `id`, `name`, `description`, `tags`, optional `examples`. |
| `securitySchemes` | Named auth schemes. Each value wraps one scheme type, for example `apiKeySecurityScheme`, `oauth2SecurityScheme`, `mtlsSecurityScheme`. |
| `securityRequirements[]` | Which schemes a caller must satisfy. Replaces 0.x `security`. |

## Why the consumer needs the card

`RemoteA2aAgent` takes the card URL, not the RPC URL:

```python
catalog = RemoteA2aAgent(
    name="catalog",
    description="Remote product catalog agent",
    agent_card=f"http://localhost:8081/a2a/product_catalog{AGENT_CARD_WELL_KNOWN_PATH}",
)
```

On first use ADK fetches the card and reads the endpoint and transport from
`supportedInterfaces`. If the card advertises the wrong URL, every call fails
even though the card itself loads.

## Common errors

| Symptom | Cause |
|---|---|
| `ParseError: ... has no field named "url" at "AgentCard"` | A 0.x card. Move `url` into `supportedInterfaces`. |
| Card fetch returns 404 | Missing `/a2a/<app_name>` prefix, or the old `agent.json` well-known path. |
