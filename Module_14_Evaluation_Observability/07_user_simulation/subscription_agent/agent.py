# Author: Vishal Bulbule
# Date: 2026-09-22

"""Subscription support agent with a retention step, the target of a user-simulation eval.

The agent looks up the subscription, offers one retention discount, and then
either applies the discount or cancels, depending on the customer's answer.
Whether a determined customer can actually get out of that funnel is a
multi-turn question with no fixed script: the customer may give the email up
front or only when asked, and may refuse the offer in any wording.

`tests/user_simulation.evalset.json` therefore uses `conversation_scenario`
eval cases. `adk eval` lets an LLM play the customer from a starting prompt,
a conversation plan and a persona, and judges the whole conversation against
rubrics in `tests/test_config.json`.
"""

from google.adk.agents import LlmAgent

SUBSCRIPTIONS = {
    "sam@example.com": {"plan": "Premium", "price_inr": 799, "renews_on": "2026-10-05"},
    "priya@example.com": {"plan": "Standard", "price_inr": 499, "renews_on": "2026-10-12"},
}


def get_subscription(email: str) -> dict:
    """Looks up the subscription for an account email.

    Args:
        email: The account email address.

    Returns:
        dict with `status` and either the subscription details or
        `error_message`.
    """
    subscription = SUBSCRIPTIONS.get(email.lower())
    if subscription is None:
        return {"status": "error", "error_message": f"No subscription for {email}."}
    return {"status": "success", "email": email.lower(), **subscription}


def apply_retention_discount(email: str) -> dict:
    """Applies 50% off the next three months. Call only after the customer accepts.

    Args:
        email: The account email address.

    Returns:
        dict with `status` and the discount details or `error_message`.
    """
    if email.lower() not in SUBSCRIPTIONS:
        return {"status": "error", "error_message": f"No subscription for {email}."}
    return {"status": "success", "email": email.lower(), "discount": "50% off for 3 months"}


def cancel_subscription(email: str) -> dict:
    """Cancels the subscription at the end of the current billing period.

    Args:
        email: The account email address.

    Returns:
        dict with `status` and the cancellation details or `error_message`.
    """
    subscription = SUBSCRIPTIONS.get(email.lower())
    if subscription is None:
        return {"status": "error", "error_message": f"No subscription for {email}."}
    return {
        "status": "success",
        "email": email.lower(),
        "subscription_status": "cancelled",
        "access_until": subscription["renews_on"],
    }


root_agent = LlmAgent(
    name="subscription_agent",
    model="gemini-3.5-flash",
    description="Handles subscription cancellations with one retention offer.",
    instruction=(
        "You handle subscription cancellations. Ask for the account email if "
        "you do not have it, then call `get_subscription`. Before cancelling, "
        "offer exactly once: 50% off for the next three months. If the "
        "customer accepts, call `apply_retention_discount`. If they decline or "
        "have already said they do not want offers, do not offer again: call "
        "`cancel_subscription` and confirm the date access ends. Keep replies "
        "to two or three sentences."
    ),
    tools=[get_subscription, apply_retention_discount, cancel_subscription],
)
