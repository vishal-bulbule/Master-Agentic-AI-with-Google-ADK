# Author: Vishal Bulbule
# Date: 2026-09-22

"""BuiltInPlanner: turn on Gemini's native thinking for an agent.

`BuiltInPlanner(thinking_config=...)` applies a `ThinkingConfig` to every
model request the agent makes. `include_thoughts=True` returns thought
summaries as event parts (marked `thought=True`), so you can inspect the
reasoning in `adk web`. `thinking_level` sets how much the model may think;
Gemini 2.5 models use `thinking_budget` (a token count) instead.

Enable thinking for multi-step reasoning (math, planning, multi-tool flows).
Skip it for simple lookups, classifiers, and high-volume endpoints, where it
adds latency and tokens for little gain.
"""

from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.genai import types


def add(a: float, b: float) -> dict:
    """Adds two numbers.

    Args:
        a: First addend.
        b: Second addend.

    Returns:
        A dict with `status` "success" and `result` equal to a + b.
    """
    return {"status": "success", "result": a + b}


def multiply(a: float, b: float) -> dict:
    """Multiplies two numbers.

    Args:
        a: First factor.
        b: Second factor.

    Returns:
        A dict with `status` "success" and `result` equal to a * b.
    """
    return {"status": "success", "result": a * b}


root_agent = LlmAgent(
    # Native thinking is a Gemini feature; other models need PlanReActPlanner.
    model="gemini-3.5-flash",
    name="thinking_math_agent",
    description="Solves multi-step math word problems using thinking + tools.",
    instruction=(
        "## Who you are\n"
        "You are a careful math tutor.\n\n"
        "## Task\n"
        "Decompose word problems into atomic steps, call `add` or `multiply` "
        "for each arithmetic step, then state the final answer.\n\n"
        "## Output\n"
        "After all tool calls, reply with: 'Answer: <number>'."
    ),
    tools=[add, multiply],
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
            thinking_level=types.ThinkingLevel.LOW,
        ),
    ),
)
