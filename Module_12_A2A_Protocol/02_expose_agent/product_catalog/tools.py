# Author: Vishal Bulbule
# Date: 2026-09-22

"""Mock product catalog tools.

They return canned data so the sample runs without a database. In a real
service these would call your commerce API.
"""

_CATALOG = {
    "SKU-1001": {
        "sku": "SKU-1001",
        "name": "Mechanical Keyboard",
        "category": "peripherals",
        "price_inr": 5499,
        "in_stock": True,
    },
    "SKU-1002": {
        "sku": "SKU-1002",
        "name": "USB-C Hub (7-in-1)",
        "category": "peripherals",
        "price_inr": 2899,
        "in_stock": True,
    },
    "SKU-2001": {
        "sku": "SKU-2001",
        "name": "Standing Desk Mat",
        "category": "office",
        "price_inr": 1899,
        "in_stock": False,
    },
    "SKU-3001": {
        "sku": "SKU-3001",
        "name": "Noise-Cancelling Headphones",
        "category": "audio",
        "price_inr": 8999,
        "in_stock": True,
    },
}


def lookup_product(sku: str) -> dict:
    """Look up a product by its SKU.

    Args:
        sku: The product SKU, for example "SKU-1001".

    Returns:
        A dict with `status` "ok" and the product (name, category, price_inr,
        in_stock), or `status` "not_found" if the SKU is unknown.
    """
    product = _CATALOG.get(sku.strip().upper())
    if not product:
        return {"status": "not_found", "sku": sku}
    return {"status": "ok", "product": product}


def list_categories() -> dict:
    """List the top-level product categories in the catalog.

    Returns:
        A dict with `status` "ok" and a sorted list of `categories`.
    """
    categories = sorted({p["category"] for p in _CATALOG.values()})
    return {"status": "ok", "categories": categories}
