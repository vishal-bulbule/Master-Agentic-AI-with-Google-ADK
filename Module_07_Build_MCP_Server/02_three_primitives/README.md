<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 02: Three Primitives

## What this shows

One server, one decorator per MCP primitive, over a small in-memory invoice
table. A URI with a `{placeholder}` becomes a resource template; the
placeholder is passed to the function as an argument.

| Decorator | Primitive | Who triggers it | Think of it as |
|---|---|---|---|
| `@mcp.tool()` | Tool | The model decides to call it | A function the model can invoke |
| `@mcp.resource("uri")` | Resource | The host reads it on demand | A file the host can attach |
| `@mcp.prompt()` | Prompt | The user picks it | A saved prompt template |

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)), virtual environment active.
- Node.js with `npx`, for MCP Inspector.
- No API keys.

## Run it

1. `cd Module_07_Build_MCP_Server/02_three_primitives`
2. `npx @modelcontextprotocol/inspector python server.py`
3. Open the URL it prints and click **Connect**.

## Try it

Tool, `search_invoices`:

1. **Tools** tab, select `search_invoices`.
2. `query` = `acme` returns INV-001. `consulting` returns INV-002.
3. `unpaid` returns nothing: status is not part of the searched text. The
   model only gets what the tool implements.

Resource, `invoice://{invoice_id}`:

1. **Resources** tab: the template `invoice://{invoice_id}` is listed under
   resource templates, not as a concrete resource.
2. Read `invoice://INV-002`: markdown with customer, amount, status, items.

Prompt, `draft_followup`:

1. **Prompts** tab, select `draft_followup`, set `invoice_id` = `INV-002`.
2. The server returns one user message: the prompt text, not the email. The
   host sends that text to the model.

## What to look for

- A host can attach resources to the context without the model deciding to
  call anything. Prompts ship the right way to ask for a task along with the
  server.
- Many servers only ship tools. ADK's `McpToolset` exposes tools by default,
  and listed (concrete) resources with `use_mcp_resources=True`; resource
  templates such as this one are not listed, so ADK cannot read them (see
  `../lab_techtrapture_mcp/` for the concrete-resource version).

Next: publish an existing ADK tool over MCP in `../03_adk_to_mcp_bridge/`.
