# Author: Vishal Bulbule
# Date: 2026-09-22

"""Recipe assistant that combines user-scoped state, session state, and memory.

State layout:
    user:dietary -> "vegetarian", "vegan", "gluten_free", ... (every session)
    cart         -> ["Paneer Tikka", "Aloo Gobi", ...]        (this session)

The `{user:dietary?}` placeholder puts the current preference into every
prompt without a tool call. The built-in `load_memory` tool lets the agent
search past sessions that were added to the memory service, for facts that
were said in conversation but never written to state (a favorite cuisine,
for example).
"""

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext, load_memory


def set_dietary(preference: str, tool_context: ToolContext) -> dict:
    """Store the user's dietary preference in user-scoped state.

    Args:
        preference: A short label such as "vegetarian", "vegan",
            "gluten_free", or "none".
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status and the stored preference.
    """
    pref = preference.strip().lower()
    tool_context.state["user:dietary"] = pref
    return {"status": "ok", "dietary": pref}


def add_recipe(name: str, tool_context: ToolContext) -> dict:
    """Append a recipe to the per-session cart.

    Args:
        name: Recipe name, for example "Paneer Tikka".
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status, the cart, and the item count.
    """
    cart = list(tool_context.state.get("cart", []))
    cart.append(name)
    tool_context.state["cart"] = cart
    return {"status": "ok", "cart": cart, "count": len(cart)}


def view_cart(tool_context: ToolContext) -> dict:
    """Return the current recipe cart.

    Args:
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status, the cart, and the item count.
    """
    cart = list(tool_context.state.get("cart", []))
    return {"status": "ok", "cart": cart, "count": len(cart)}


def clear_cart(tool_context: ToolContext) -> dict:
    """Empty the recipe cart.

    Args:
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status and the empty cart.
    """
    tool_context.state["cart"] = []
    return {"status": "ok", "cart": []}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="recipe_assistant",
    description="Suggests and tracks recipes, respecting dietary preferences.",
    instruction=(
        "You are a personal recipe assistant. The user's dietary preference "
        "is {user:dietary?}. Always respect it when suggesting recipes.\n\n"
        "Tools:\n"
        "  - set_dietary(preference): when the user states or changes a "
        "diet (vegetarian, vegan, gluten_free, none).\n"
        "  - add_recipe(name): when the user wants a recipe in their cart.\n"
        "  - view_cart(): when the user asks what is in their cart.\n"
        "  - clear_cart(): when the user asks to empty the cart.\n"
        "  - load_memory(query): before suggesting a recipe, search past "
        "conversations for tastes the user mentioned, such as a favorite "
        "cuisine. Use plain words the user would have said, for example "
        "'food cuisine love like', because the local memory service matches "
        "keywords, not meaning.\n\n"
        "Confirm every action in one short sentence."
    ),
    tools=[set_dietary, add_recipe, view_cart, clear_cart, load_memory],
)
