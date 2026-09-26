# Author: Vishal Bulbule
# Date: 2026-09-22

"""Sub-agent handoff: the coordinator transfers the conversation to billing.

`billing_specialist` is passed in `sub_agents`, so the coordinator can call
`transfer_to_agent` to hand it the conversation. After the transfer, billing
replies to the user directly and keeps receiving the user's next messages
until it transfers back. Compare with `translator_demo`, where the helper
agent is a tool and the coordinator always writes the reply.
"""

from google.adk.agents import LlmAgent

MODEL = "gemini-3.5-flash"


billing_specialist = LlmAgent(
    model=MODEL,
    name="billing_specialist",
    description=(
        "Handles all billing questions: invoices, refunds, payment failures, "
        "subscription changes. Owns the conversation once engaged."
    ),
    instruction=(
        "You are the billing specialist. Greet the user warmly, acknowledge "
        "you've taken over from the coordinator, and walk them through their "
        "billing issue step by step. Ask one clarifying question at a time."
    ),
)


root_agent = LlmAgent(
    model=MODEL,
    name="support_coordinator",
    description="General support agent that delegates billing to a specialist.",
    instruction=(
        "You are the front-line support agent. Answer general questions "
        "(account access, product features, how-to) yourself.\n\n"
        "If the user mentions billing, invoices, refunds, charges, "
        "subscriptions, or payment methods, hand off immediately by calling "
        "transfer_to_agent(agent_name='billing_specialist'). Do not try to "
        "answer billing questions yourself."
    ),
    sub_agents=[billing_specialist],
)
