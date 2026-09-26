# Author: Vishal Bulbule
# Date: 2026-09-22

"""Writer and critic in a refinement loop, built as a Workflow graph.

The loop is an ordinary edge that points back to an earlier node. A cycle
needs at least one routed edge, so a small function node, `decide_next_step`,
emits either the "revise" route (back to the writer) or the "done" route
(to `publish`). This replaces the deprecated `LoopAgent`, whose
`max_iterations` and `escalate` exit become plain Python in that function.

The loop's working keys use the `temp:` prefix, so every new request starts
with an empty draft and a fresh round counter. Only the approved text is
written to a normal session key, `final_draft`.
"""

from google.adk import Context, Event, Workflow
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

MODEL = "gemini-3.5-flash"
MAX_ROUNDS = 3


def approve_draft(tool_context: ToolContext) -> dict:
    """Mark the current draft as good enough to publish.

    Args:
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with the new review status.
    """
    tool_context.state["temp:review_status"] = "approved"
    return {"status": "approved"}


writer = LlmAgent(
    model=MODEL,
    name="writer",
    description="Drafts or revises the paragraph the user asked for.",
    instruction=(
        "You are a writer. Produce a single paragraph on the topic in the "
        "input.\n"
        "If there is an existing draft below, revise it to address the "
        "critique. Otherwise, write a first draft.\n\n"
        "Existing draft (may be empty): {temp:current_draft?}\n"
        "Critique to address (may be empty): {temp:critique?}\n\n"
        "Output only the paragraph, with no preface or commentary."
    ),
    output_key="temp:current_draft",
)

critic = LlmAgent(
    model=MODEL,
    name="critic",
    description="Critiques the current draft or approves it.",
    instruction=(
        "You are a tough editor. Read the current draft:\n\n"
        "{temp:current_draft}\n\n"
        "Approve it only if all of these hold: it is under 90 words, it "
        "includes one concrete example, and it avoids hype words such as "
        "'transformative', 'revolutionary', or 'game-changing'.\n"
        "If it passes, call the approve_draft tool and reply with the single "
        "word APPROVED.\n"
        "Otherwise, do not call the tool. Reply with a short critique "
        "(2-3 bullets) that the writer can act on."
    ),
    tools=[approve_draft],
    output_key="temp:critique",
)


def decide_next_step(ctx: Context) -> Event:
    """Route back to the writer, or finish when approved or out of rounds."""
    rounds = ctx.state.get("temp:rounds", 0) + 1
    approved = ctx.state.get("temp:review_status") == "approved"
    if approved or rounds >= MAX_ROUNDS:
        return Event(route="done", state={"temp:rounds": rounds})
    critique = ctx.state.get("temp:critique", "")
    return Event(
        output=f"Revise the draft to address this critique:\n{critique}",
        route="revise",
        state={"temp:rounds": rounds},
    )


def publish(ctx: Context) -> Event:
    """Store the final draft in session state and show it to the user."""
    draft = ctx.state.get("temp:current_draft", "")
    rounds = ctx.state.get("temp:rounds", 0)
    return Event(
        message=f"Final draft after {rounds} round(s):\n\n{draft}",
        state={"final_draft": draft},
    )


root_agent = Workflow(
    name="quality_loop",
    description="Writes and critiques a paragraph until it is approved.",
    edges=[
        ("START", writer, critic, decide_next_step),
        (decide_next_step, {"revise": writer, "done": publish}),
    ],
)
