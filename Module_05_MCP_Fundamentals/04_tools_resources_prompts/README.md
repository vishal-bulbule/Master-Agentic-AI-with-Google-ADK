<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 04: Tools, Resources, Prompts

## What this shows

One server that exposes all three MCP primitives over a small in-memory
invoice table. The difference between them is who triggers them, not what
they return: tools are verbs, resources are nouns, prompts are templates.

| Primitive | Who triggers it | Typical use | In this server |
|---|---|---|---|
| Tool | The model | Do something: send a message, search invoices | `search_invoices(customer, status)` |
| Resource | The host or the user | Attach readable data as context | `invoice://{invoice_id}` |
| Prompt | The user | Pick a reusable instruction template | `draft_followup(invoice_id, tone)` |

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)), virtual environment active.
- Node.js with `npx`, for MCP Inspector.
- No API keys.

## Run it

1. `cd Module_05_MCP_Fundamentals/04_tools_resources_prompts`
2. `npx @modelcontextprotocol/inspector python server.py`
3. Open the URL Inspector prints and click **Connect**.

The same three calls without a browser:

```bash
npx @modelcontextprotocol/inspector --cli python server.py \
  --method tools/call --tool-name search_invoices --tool-arg status=overdue
npx @modelcontextprotocol/inspector --cli python server.py \
  --method resources/read --uri invoice://INV-002
npx @modelcontextprotocol/inspector --cli python server.py \
  --method prompts/get --prompt-name draft_followup --prompt-args invoice_id=INV-002
```

## What to look for

- **Tools**: run `search_invoices` with `status` = `overdue`. You get INV-002
  and INV-004.
- **Resources**: open **Resource Templates**, pick `invoice://{invoice_id}`,
  and read `invoice://INV-002`. You get markdown, not JSON: resources are
  content for the context window.
- **Prompts**: `draft_followup` with `invoice_id` = `INV-002`. The server
  returns the prompt text, not an email. The host inserts that text into the
  conversation and the model writes the email.

How a host presents prompts and resources varies: some show prompts as slash
commands or in an attachment menu, some ignore resources entirely. Tools are
the one primitive every host supports.

Choosing a primitive:

1. Should the model call it on its own? Tool.
2. Is it data you want attached as context, without the model fetching it
   autonomously? Resource.
3. Is it a workflow the user starts explicitly? Prompt.

When in doubt, start with a tool. It has the widest host support and maps
directly to Gemini function calling.
