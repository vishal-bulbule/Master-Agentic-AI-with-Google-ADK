# Author: Vishal Bulbule
# Date: 2026-09-22

"""RetryAgent: a custom BaseAgent that re-runs a flaky sub-agent.

Subclass `BaseAgent` and implement `_run_async_impl` when you want to write the
control flow yourself. This one runs its single sub-agent up to `max_attempts`
times and stops as soon as the sub-agent reports success in session state.

Every state change the orchestrator makes is yielded as an event with a
`state_delta`. Assigning to `ctx.session.state` directly is not recorded in
the session, so the value would be missing when you inspect it later.
"""

from typing import AsyncGenerator

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.tools import ToolContext

MODEL = "gemini-3.5-flash"


def call_flaky_service(tool_context: ToolContext) -> dict:
    """Call a simulated service that fails on attempts 1 and 2, then succeeds.

    Args:
        tool_context: Injected by ADK; the tool reads the attempt number from
            state and writes the outcome back.

    Returns:
        A dict with status "error" or "ok", the attempt number, and either an
        error message or the order data.
    """
    attempt = int(tool_context.state.get("attempt", 1))
    if attempt < 3:
        tool_context.state["flaky_status"] = "error"
        return {
            "status": "error",
            "attempt": attempt,
            "message": f"transient failure on attempt {attempt}",
        }
    tool_context.state["flaky_status"] = "ok"
    return {
        "status": "ok",
        "attempt": attempt,
        "data": {"order_id": "ORD-42", "total": 199},
    }


flaky_agent = LlmAgent(
    model=MODEL,
    name="flaky_agent",
    description="Calls the flaky service once and reports the result.",
    instruction=(
        "This is attempt {attempt}. Call the call_flaky_service tool exactly "
        "once for this attempt, even if earlier attempts appear in the "
        "conversation. Then write one short sentence describing the outcome "
        "(success or transient failure, with the attempt number). Do not "
        "retry yourself; your parent agent does that."
    ),
    tools=[call_flaky_service],
)


class RetryAgent(BaseAgent):
    """Re-runs its single sub-agent up to `max_attempts` times.

    Stops early when `state["flaky_status"] == "ok"`. The current attempt
    number is written to `state["attempt"]` so the tool can read it.
    """

    max_attempts: int = 3

    def _state_event(self, ctx: InvocationContext, delta: dict) -> Event:
        return Event(
            author=self.name,
            invocation_id=ctx.invocation_id,
            actions=EventActions(state_delta=delta),
        )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        inner = self.sub_agents[0]
        yield self._state_event(ctx, {"flaky_status": "pending"})

        for attempt in range(1, self.max_attempts + 1):
            yield self._state_event(ctx, {"attempt": attempt})
            async for event in inner.run_async(ctx):
                yield event

            if ctx.session.state.get("flaky_status") == "ok":
                yield self._state_event(
                    ctx,
                    {
                        "retry_summary": (
                            f"Succeeded on attempt {attempt} of "
                            f"{self.max_attempts}."
                        )
                    },
                )
                return

        yield self._state_event(
            ctx,
            {"retry_summary": f"Gave up after {self.max_attempts} attempts."},
        )


root_agent = RetryAgent(
    name="retry_demo",
    description="Retries a flaky sub-agent up to 3 times until it succeeds.",
    sub_agents=[flaky_agent],
)
