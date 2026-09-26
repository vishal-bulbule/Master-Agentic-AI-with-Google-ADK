<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 01: The M x N Problem

## What this shows

Before MCP, every LLM application built its own integration for every
external service: 5 apps and 10 services meant up to 50 custom adapters, each
with its own auth, error handling, retries, and tool schema. MCP turns the
product into a sum: each service writes one MCP server, each application
writes one MCP client (or runs inside a host that has one), and any client can
use any server. 5 apps and 10 services become 15 things to build. The two
scripts simulate both shapes in plain Python, with no network calls.

Before MCP (M x N):

```
            Slack    GitHub   Postgres  Notion   Stripe
            -----    ------   --------  ------   ------
App A  -->   [A1]    [A2]     [A3]      [A4]     [A5]
App B  -->   [B1]    [B2]     [B3]      [B4]     [B5]
App C  -->   [C1]    [C2]     [C3]      [C4]     [C5]
App D  -->   [D1]    [D2]     [D3]      [D4]     [D5]
App E  -->   [E1]    [E2]     [E3]      [E4]     [E5]

   5 apps x 5 services = 25 custom adapters.
   Each box has its own auth, retry, schema, and test code.
```

After MCP (M + N):

```
                              +-----------------------+
   App A --+                  |  MCP Slack server     |
   App B --+                  +-----------------------+
   App C --+--> MCP client -->|  MCP GitHub server    |
   App D --+    (one per      +-----------------------+
   App E --+     host)        |  MCP Postgres server  |
                              +-----------------------+
                              |  MCP Notion server    |
                              +-----------------------+
                              |  MCP Stripe server    |
                              +-----------------------+

   5 apps + 5 services = 10 things to build.
   Every app speaks the same protocol to every server.
```

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). No API keys:
neither script calls a model.

## Run it

1. `cd Module_05_MCP_Fundamentals/01_mn_problem_diagram`
2. `python before.py`
3. `python after.py`

## What to look for

- `before.py`: three apps each ship their own Slack adapter. The method
  names, argument names, and tool schemas all differ for the same capability.
- `after.py`: one server advertises one schema, and all three apps call it
  through the same client interface.

Both scripts show the shape of the problem, not the MCP wire protocol; that
starts in `../03_fastmcp_first_server/`.
