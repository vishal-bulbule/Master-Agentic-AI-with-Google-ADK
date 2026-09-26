# Author: Vishal Bulbule
# Date: 2026-09-22

"""Tools, resources, and prompts in one FastMCP server.

One decorator per primitive: `@mcp.tool()` for actions the model calls,
`@mcp.resource(uri)` for data the host reads like a file, `@mcp.prompt()` for
templates the user picks. A URI with a `{placeholder}` becomes a resource
template; the placeholder is passed to the function as an argument.

Run:
    python server.py
Inspect:
    npx @modelcontextprotocol/inspector python server.py
"""

from fastmcp import FastMCP

mcp = FastMCP("invoice-server")

# In-memory stand-in for a billing system, so the server is self-contained.
_INVOICES = {
    "INV-001": {"customer": "Acme Corp", "amount": 12000, "status": "paid", "items": ["ADK Workshop"]},
    "INV-002": {"customer": "Globex Inc", "amount": 8500, "status": "unpaid", "items": ["MCP Consulting"]},
    "INV-003": {"customer": "Initech", "amount": 4200, "status": "unpaid", "items": ["Gemini Training"]},
}


@mcp.tool()
def search_invoices(query: str) -> dict:
    """Search invoices by free text against customer name and line items.

    Args:
        query: Case-insensitive text to find, for example "acme" or "consulting".

    Returns:
        A dict with status and the list of matching invoices.
    """
    q = query.lower()
    hits = []
    for invoice_id, invoice in _INVOICES.items():
        haystack = (invoice["customer"] + " " + " ".join(invoice["items"])).lower()
        if q in haystack:
            hits.append({"id": invoice_id, **invoice})
    return {"status": "success", "invoices": hits}


@mcp.resource("invoice://{invoice_id}")
def read_invoice(invoice_id: str) -> str:
    """The full invoice as markdown."""
    invoice = _INVOICES.get(invoice_id)
    if not invoice:
        return f"# Invoice {invoice_id}\n\n_Not found._"
    items = "\n".join(f"- {item}" for item in invoice["items"])
    return (
        f"# Invoice {invoice_id}\n\n"
        f"**Customer:** {invoice['customer']}\n"
        f"**Amount:** INR {invoice['amount']:,}\n"
        f"**Status:** {invoice['status']}\n\n"
        f"## Items\n{items}\n"
    )


@mcp.prompt()
def draft_followup(invoice_id: str) -> str:
    """Polite follow-up email for an unpaid invoice."""
    return (
        "Draft a polite, professional follow-up email for unpaid invoice "
        f"{invoice_id}. Use the invoice resource at invoice://{invoice_id} "
        "for the amount and customer details. Keep it under 120 words."
    )


if __name__ == "__main__":
    mcp.run()
