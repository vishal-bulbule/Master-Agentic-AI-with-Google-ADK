<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 10: The same call, with ADK

## What this shows

`../04_function_calling/function_calling.py` runs the tool loop by hand: it
reads the `function_call` part, runs the function, appends a
`function_response` part, and calls the model a second time. This topic is the
same weather task as an ADK agent. The tool is identical; the loop is gone.
It is the bridge from the raw SDK to the rest of the repository, where every
sample is an agent.

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)): the virtual
environment and credentials in a `.env` at the repository root, or in this
agent folder using the variables from
[`weather_agent/.env.example`](weather_agent/.env.example).

## Run it

1. `cd Module_00_AI_Foundations/10_same_call_with_adk`
2. `adk web`
3. Open http://localhost:8000 and pick `weather_agent` in the app dropdown in
   the top bar.
4. Send: "What's the weather in Mumbai?"

Terminal alternative: `adk run weather_agent`.

## Try it

| Prompt | What happens |
|---|---|
| "What's the weather in Mumbai?" | One `get_weather` call, then the answer |
| "Compare Paris and Tokyo" | Two `get_weather` calls in one turn, which the handwritten loop in topic 04 does not handle |
| "What's the weather in Lagos?" | The tool returns an error and the agent says it has no data, instead of inventing a temperature |

## What to look for

- In the Events view, the numbered rows are the same steps topic 04 printed:
  the tool call with its arguments, the tool result, then the answer. Click a
  row to see the full JSON in the side panel.
- `agent.py` has no history handling and no second model call. ADK runs the
  loop for as many rounds as the model needs, which is why the comparison
  prompt works without extra code.
- The tool declaration the model sees is still built from the function name,
  type hints and docstring, exactly as in the raw SDK version.

## Clean up

`adk web` and `adk run` store sessions in `weather_agent/.adk/`. Remove it
with `rm -rf weather_agent/.adk`.
