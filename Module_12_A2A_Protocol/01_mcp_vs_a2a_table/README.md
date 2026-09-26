<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 01: MCP vs A2A

## What this shows

MCP and A2A are two protocols with different jobs. MCP connects an agent to a
tool or data source; A2A connects an agent to another agent that has its own
model. This page compares them and walks through one request that needs both.

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)).

## Run it

Nothing to run; this is a reference page. Topics 02 to 04 run the A2A side.

## What to look for

The comparison below, and the worked example: which part of the request is a
function (MCP) and which part needs another agent's judgment (A2A).

## Comparison

| | MCP | A2A |
|---|---|---|
| Connects | Agent to a tool or data source | Agent to another agent |
| The other side | Runs a function and returns structured data | Runs its own model: judgment, planning, follow-up questions |
| Created by | Anthropic (now a Linux Foundation project) | Google (now a Linux Foundation project) |
| Use when | A service should expose tools | Another agent should own a task end to end |
| Transport | stdio or Streamable HTTP | HTTP: JSON-RPC, HTTP+JSON, or gRPC |
| Auth | Configured by the client, per server | Declared in the agent card (API key, OAuth2, OIDC, mTLS) |
| State | Mostly stateless calls | Stateful tasks (`SUBMITTED`, `WORKING`, `INPUT_REQUIRED`, `COMPLETED`) |
| Discovery | `tools/list` | Agent card at `/.well-known/agent-card.json` |

Rule of thumb: if the other side has its own model and makes decisions, use
A2A. If it is a function, use MCP.

## When A2A fits

- The other agent is a separate service maintained by another team.
- You need to cross a language boundary (a Python agent calling a Java agent).
- You want a versioned contract at the agent boundary (the agent card).
- Each domain owns its agent, its data, and its model choice.

## When it does not

- The other agent runs in the same process: use `sub_agents=[...]` or
  `AgentTool` directly.
- The call is latency-critical: every A2A hop adds a network round trip and a
  second model call.
- You only want to organize code: use Python modules or local sub-agents.

## Worked example

One request needs both protocols:

> Look up issue #482 on the `acme/api` repo and check whether the customer who
> filed it has an open invoice.

### GitHub data: MCP

Reading an issue is a function, `get_issue(repo, number)`. The GitHub MCP
server exposes it as a tool. The agent calls it and gets deterministic JSON
back, with no second model involved.

```python
github = McpToolset(connection_params=...)  # GitHub MCP server
root_agent = LlmAgent(..., tools=[github])
```

### Open invoice: A2A

This is not a function. The billing team runs an agent that matches the
customer by email or domain, decides which invoices count as open given
partial payments and disputes, applies the company's invoice policy, and may
ask a follow-up question ("include disputed invoices?"). That belongs behind
A2A, where the billing team owns the prompt and the policy and versions the
agent on its own schedule.

```python
billing = RemoteA2aAgent(
    name="billing_specialist",
    agent_card=f"https://billing.example.com{AGENT_CARD_WELL_KNOWN_PATH}",
)
root_agent = LlmAgent(..., tools=[github], sub_agents=[billing])
```

### Combined flow

```
User: "Look up issue #482 and check if the customer has an open invoice."

              root agent (LlmAgent)
               |                 |
          MCP tool call      A2A sub-agent
          get_issue()        billing_specialist
          returns JSON       reasons, may ask a follow-up
```

Do not expose every function as an A2A agent; the protocol and the extra
model call cost more than a tool call. Do not expose billing policy as an MCP
tool; the calling model would have to reason about policy it does not own.
