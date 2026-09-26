<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 04 Custom BaseAgent (RetryAgent)

## What this shows

`RetryAgent` subclasses `BaseAgent` and implements `_run_async_impl` to run a
flaky sub-agent up to three times, stopping once the sub-agent reports
success. The simulated service fails on attempts 1 and 2 and succeeds on 3.
`_run_async_impl` is an async generator that yields `Event` objects, runs a
sub-agent with `async for event in sub.run_async(ctx): yield event`, and
writes state by yielding an event with `EventActions(state_delta=...)`.
Assigning to `ctx.session.state` directly is not recorded in the session.
`BaseAgent` subclassing is still supported in ADK 2.x; the docs now point to
`Workflow` first (a routed loop as in `03_loop_refinement`, or a node with
`retry_config=RetryConfig(max_attempts=3)` for retrying on exceptions). Use a
custom `BaseAgent` when the agent itself must be a reusable class.

```python
class RetryAgent(BaseAgent):
    max_attempts: int = 3

    async def _run_async_impl(self, ctx):
        inner = self.sub_agents[0]
        for attempt in range(1, self.max_attempts + 1):
            yield self._state_event(ctx, {"attempt": attempt})
            async for event in inner.run_async(ctx):
                yield event
            if ctx.session.state.get("flaky_status") == "ok":
                return
```

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials
go in a `.env` at the repository root or in the agent folder; see
`retry_demo/.env.example` (Gemini API key, or Agent Platform (formerly
Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_09_Workflow_MultiAgent/04_custom_base_agent`
2. `adk web`
3. Open http://localhost:8000 and select `retry_demo`.
4. Send: `Call the flaky service and report the result.`

Terminal alternative: `adk run retry_demo`.

## What to look for

- Events view: `retry_demo` state events (`attempt: 1`, `2`, `3`) between three
  `call_flaky_service` calls from `flaky_agent`: two errors, then success.
- State tab: `attempt: 3`, `flaky_status: "ok"`, and
  `retry_summary: "Succeeded on attempt 3 of 3."`.

## Clean up

Sessions are kept in `retry_demo/.adk/session.db`. Delete it to start clean:
`rm -rf retry_demo/.adk`
