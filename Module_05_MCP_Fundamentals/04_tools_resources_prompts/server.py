# Author: Vishal Bulbule
# Date: 2026-09-22

"""All three MCP primitives in one server.

- Tool (the model decides to call it): search_invoices
- Resource (the host or user attaches it as context): invoice://{invoice_id}
- Prompt (the user picks it as a template): draft_followup

The difference between them is who triggers them, not what they return.
Inspector shows each one in its own tab.

Run:
    python server.py
Inspect:
    npx @modelcontextprotocol/inspector python server.py
"""

from fastmcp import FastMCP

mcp = FastMCP("invoices-demo")

# In-memory stand-in for a billing database.
INVOICES = {
    "INV-001": {"customer": "Acme Corp", "amount": 12000, "status": "paid"},
    "INV-002": {"customer": "Globex Ltd", "amount": 4500, "status": "overdue"},
    "INV-003": {"customer": "Initech", "amount": 9800, "status": "sent"},
    "INV-004": {"customer": "Acme Corp", "amount": 3000, "status": "overdue"},
}


@mcp.tool()
def search_invoices(customer: str | None = None, status: str | None = None) -> dict:
    """Search invoices by customer name and/or status.

    Use this when the user asks questions like "which invoices are overdue"
    or "show me Acme's bills".

    Args:
        customer: Case-insensitive substring of the customer name. Optional.
        status: Exact invoice status: paid, sent, or overdue. Optional.

    Returns:
        A dict with status and the list of matching invoices.
    """
    matches = []
    for invoice_id, row in INVOICES.items():
        if customer and customer.lower() not in row["customer"].lower():
            continue
        if status and status.lower() != row["status"].lower():
            continue
        matches.append({"id": invoice_id, **row})
    return {"status": "success", "invoices": matches}


@mcp.resource("invoice://{invoice_id}")
def get_invoice(invoice_id: str) -> str:
    """One invoice as markdown, for example invoice://INV-001."""
    row = INVOICES.get(invoice_id)
    if not row:
        return f"# {invoice_id}\n\nNot found."
    return (
        f"# Invoice {invoice_id}\n\n"
        f"- Customer: {row['customer']}\n"
        f"- Amount:   INR {row['amount']:,}\n"
        f"- Status:   {row['status']}\n"
    )


@mcp.prompt()
def draft_followup(invoice_id: str, tone: str = "polite") -> str:
    """Draft a follow-up email for an overdue invoice."""
    return (
        "You are an accounts-receivable assistant.\n\n"
        f"Draft a {tone} follow-up email about invoice {invoice_id}. "
        f"Use the resource invoice://{invoice_id} for the details. "
        "Keep it under 120 words. Sign off as 'Accounts team'."
    )


if __name__ == "__main__":
    mcp.run()
