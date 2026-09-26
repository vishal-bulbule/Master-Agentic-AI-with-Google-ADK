<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 01: Anatomy of a Good Tool

## What this shows

Two agents do the same job, looking up an order in the same in-memory order
book. The only real difference is how their tool is written.

`agent/agent.py` exposes `lookup_order_status(order_id)`, which follows five
rules:

1. Descriptive name: `lookup_order_status`, not `do_thing`.
2. Type hints on every parameter (`order_id: str`) and the return value.
3. The docstring tells the model when to call the tool, not only what it does.
4. It returns a dict with a `status` field: `success` or `error`.
5. Error messages are sentences the model can act on ("Ask the user to re-check the ID.").

`bad_tool_agent/agent.py` exposes `do_thing(x, y=None)`, which breaks all
five: vague name, no type hints, no docstring, returns the raw record or
`None`, and has no error handling. Its instruction does not name the tool, so
the model has only the tool declaration to go on.

ADK builds the declaration the model sees from three things only: the
function name, the type-hinted parameters, and the docstring. The dev UI
shows that declaration for every model call, so you can compare the two
side by side.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`agent/.env.example`](agent/.env.example) (the same
      for `bad_tool_agent`): `GOOGLE_API_KEY`, or Agent Platform (formerly
      Vertex AI) with `GOOGLE_CLOUD_LOCATION=global` (`gemini-3.5-flash` is
      served from `global`).

## Run it

1. `cd Module_04_Custom_Tools/01_anatomy_of_a_tool`
2. `adk web`
3. Open http://localhost:8000 and pick `agent` in the app dropdown in the top bar.
4. Send: "What's the status of A-1001?"
5. Pick `bad_tool_agent` in the app dropdown, click **New Session**, and send
   the same prompt.

Terminal alternative: `adk run agent` and `adk run bad_tool_agent`.

## Try it

Send each prompt to both agents, in a new session each time.

| Prompt | `agent` | `bad_tool_agent` |
|---|---|---|
| "What's the status of A-1001?" | `lookup_order_status("A-1001")`, success | Usually `do_thing("A-1001")` and the right answer: with one tool and an obvious ID, the model often guesses right. |
| "Has order 1002 shipped?" | Asks for the full ID, or calls with `A-1002` (the docstring shows the format) | Guesses: `do_thing("1002")`, then calls like `do_thing("order", 1002)` or `do_thing("1002", "shipped")`, until the safety cap stops the turn after 5 calls. |
| "Check order Z-9999" | `status: error` with a message; the agent asks you to re-check the ID | The response is `{"result": null}`; the agent has to guess why. |
| "Where's my stuff?" | Asks for the order ID, no tool call | Usually asks too. |

Model behaviour varies from run to run; the guessing on the bad tool is the
point, not the exact calls.

## What to look for

- Events view: the tool call chips. `lookup_order_status("A-1001")` against
  `do_thing("A-1001")`, and on "Has order 1002 shipped?" the list of guessed
  `do_thing` calls with arguments that change type and meaning from call to
  call.
- The Request view: click the tool call row (`#2`), then the third icon in
  the icon strip on the left of the side panel (tooltip **Request**). It shows
  the request sent to the model, including `tools > function_declarations`:
  - `agent`: `name`, a `description` taken from the docstring, and
    `order_id` with `type: "string"`.
  - `bad_tool_agent`: `name: "do_thing"`, no `description`, and parameters
    `x` and `y` with a `title` but no `type`. That is everything the model
    knows about the tool.
- Click a tool result row to compare the responses in the side panel:
  `status` and `error_message` against a bare record or `null`.

| Symptom on the bad tool | Cause |
|---|---|
| Tool not called, or called in the wrong situation | No description, so the model has no reason to call it and no hint about when. |
| Called with random strings, numbers, or lists | No type hints, so the schema has no types and the model guesses. |
| Retries the same lookup many ways | `None` says nothing about what went wrong; an error message would tell the model to stop and ask. |

## Common errors

| Symptom | Cause |
|---|---|
| `bad_tool_agent` replies "Stopped after 5 tool calls without an answer" | The model kept guessing arguments for `do_thing`. A safety cap in the agent (`stop_runaway_calls`) ends the turn so the demo cannot loop; it is not part of the lesson. |
