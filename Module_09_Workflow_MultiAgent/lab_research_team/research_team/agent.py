# Author: Vishal Bulbule
# Date: 2026-09-22

"""Research team lab: plan, research in parallel, write, then critique in a loop.

One `Workflow` graph combines every pattern from this module:

    START -> planner -> (researcher_1, researcher_2, researcher_3)
          -> wait_for_findings -> writer -> critic -> decide_next_step
    decide_next_step --"revise"--> writer
    decide_next_step --"done"----> publish

The planner's tool writes three sub-questions to state. The fan-out runs the
three researchers concurrently, the `JoinNode` waits for all of them, and the
writer/critic cycle replaces the deprecated `LoopAgent`. In a Workflow the
same `writer` node can be reached from two edges, so the ADK 1.x workaround of
building a second writer instance is no longer needed.
"""

from google.adk import Context, Event, Workflow
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from google.adk.workflow import JoinNode

MODEL = "gemini-3.5-flash"
MAX_ROUNDS = 3


def save_sub_questions(q1: str, q2: str, q3: str, tool_context: ToolContext) -> dict:
    """Store the three sub-questions in state for the parallel researchers.

    Args:
        q1: First sub-question.
        q2: Second sub-question.
        q3: Third sub-question.
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status and the saved sub-questions.
    """
    questions = [q1.strip(), q2.strip(), q3.strip()]
    for index, question in enumerate(questions, start=1):
        tool_context.state[f"subq_{index}"] = question
    tool_context.state["sub_questions"] = questions
    return {"status": "ok", "sub_questions": questions}


planner = LlmAgent(
    model=MODEL,
    name="planner",
    description="Splits the topic into exactly 3 well-scoped sub-questions.",
    instruction=(
        "You are a research planner. The input is a research topic. "
        "Decompose it into exactly three focused, non-overlapping "
        "sub-questions that together cover the topic.\n\n"
        "Call the save_sub_questions tool once with q1, q2, q3 set to the "
        "three sub-questions. After the tool call, list the three "
        "sub-questions briefly."
    ),
    tools=[save_sub_questions],
    output_key="planner_notes",
)


def mock_search(sub_question: str) -> dict:
    """Return canned findings so the lab runs without a search API.

    Args:
        sub_question: The specific sub-question to investigate.

    Returns:
        A dict with status, the sub-question, and a list of result strings.
    """
    sq = (sub_question or "").strip()
    return {
        "status": "ok",
        "sub_question": sq,
        "results": [
            f"Result A: Authoritative source addresses '{sq}'.",
            f"Result B: A 2026 article touching on '{sq}'.",
            f"Result C: Practitioner blog post relevant to '{sq}'.",
        ],
        "note": "Mock results. Replace mock_search with a real search tool.",
    }


def _researcher(index: int) -> LlmAgent:
    """Build the researcher for sub-question `index` (1-based)."""
    return LlmAgent(
        model=MODEL,
        name=f"researcher_{index}",
        description=f"Researches sub-question {index}.",
        instruction=(
            f"You are researcher {index}. Your sub-question is:\n\n"
            f"{{subq_{index}}}\n\n"
            "Call mock_search(sub_question=<that sub-question>) once, then "
            "summarize the results in 3-4 bullets. Use only what the results "
            "say and do not add facts from your own knowledge; the results "
            "are mock data, so say so if they do not answer the question."
        ),
        tools=[mock_search],
        output_key=f"findings_{index}",
    )


researchers = (_researcher(1), _researcher(2), _researcher(3))
wait_for_findings = JoinNode(name="wait_for_findings")

writer = LlmAgent(
    model=MODEL,
    name="writer",
    description="Assembles the three findings into a structured report.",
    instruction=(
        "Write a clear research report.\n\n"
        "Sub-question 1: {subq_1}\nFindings 1:\n{findings_1}\n\n"
        "Sub-question 2: {subq_2}\nFindings 2:\n{findings_2}\n\n"
        "Sub-question 3: {subq_3}\nFindings 3:\n{findings_3}\n\n"
        "Previous draft (may be empty):\n{temp:draft_report?}\n\n"
        "Critique to address (may be empty):\n{temp:critique?}\n\n"
        "Produce a one-line summary, then three sections (one per "
        "sub-question), then a short 'Bottom line' paragraph. Use only the "
        "findings above and do not invent facts."
    ),
    output_key="temp:draft_report",
)


def approve_report(tool_context: ToolContext) -> dict:
    """Mark the current draft report as ready to publish.

    Args:
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with the new review status.
    """
    tool_context.state["temp:review_status"] = "approved"
    return {"status": "approved"}


critic = LlmAgent(
    model=MODEL,
    name="critic",
    description="Critiques the draft report or approves it.",
    instruction=(
        "You are a tough editor. Read the current draft report:\n\n"
        "{temp:draft_report}\n\n"
        "If it is clear, well structured, and faithful to the findings, call "
        "the approve_report tool and reply with the single word APPROVED.\n"
        "Otherwise, do not call the tool. Reply with a short critique "
        "(2-3 bullets) that the writer can act on."
    ),
    tools=[approve_report],
    output_key="temp:critique",
)


def decide_next_step(ctx: Context) -> Event:
    """Route back to the writer, or finish when approved or out of rounds."""
    rounds = ctx.state.get("temp:rounds", 0) + 1
    approved = ctx.state.get("temp:review_status") == "approved"
    if approved or rounds >= MAX_ROUNDS:
        return Event(route="done", state={"temp:rounds": rounds})
    return Event(
        output="Revise the report to address the critique.",
        route="revise",
        state={"temp:rounds": rounds},
    )


def publish(ctx: Context) -> Event:
    """Save the final report to session state and show it to the user."""
    report = ctx.state.get("temp:draft_report", "")
    return Event(
        message=report,
        state={
            "final_report": report,
            "review_rounds": ctx.state.get("temp:rounds", 0),
        },
    )


root_agent = Workflow(
    name="research_team",
    description=(
        "Plans the topic into 3 sub-questions, researches them in parallel, "
        "writes a report, and refines it with a critic loop."
    ),
    edges=[
        ("START", planner, researchers),
        (researchers, wait_for_findings),
        (wait_for_findings, writer, critic, decide_next_step),
        (decide_next_step, {"revise": writer, "done": publish}),
    ],
)
