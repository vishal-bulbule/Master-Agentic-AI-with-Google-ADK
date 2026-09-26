<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Instruction Patterns

## What this shows

Three sibling agents with the same tool and the same model; only the
`instruction` string changes. A vague instruction leaves the model to fill
gaps from memory, a structured one (who, task, tools, output format) makes
the behavior predictable, and a templated one pulls a value from session
state into the prompt.

| Subfolder | What it shows |
|---|---|
| `bad_instruction/` | Vague instruction. The agent fills gaps from memory. |
| `good_instruction/` | Structured instruction: who, task, tools, output format. |
| `templated_instruction/` | `{user_name?}` placeholder filled from session state. |

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and credentials.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from any subfolder's `.env.example`: `GOOGLE_API_KEY`,
      or Agent Platform (formerly Vertex AI) with
      `GOOGLE_CLOUD_LOCATION=global` (`gemini-3.5-flash` is served from
      `global`).

## Run it

1. `cd Module_03_LlmAgent_Model_Choice/instruction_patterns`
2. `adk web`
3. Open http://localhost:8000 and select `bad_instruction` in the agent dropdown.
4. Send: "What's the capital of Germany?"
5. Select `good_instruction` and send the same prompt.

Terminal alternative: `adk run bad_instruction` and `adk run good_instruction`.

## Try it

Send each prompt to `bad_instruction` and to `good_instruction`:

- "What's the capital of France?" (in the tool's data)
- "What's the capital of Germany?" (not in the tool's data; the tool returns an error)
- "Tell me about Japan." (open-ended)

Then the templated agent:

1. Select `templated_instruction` and send "What is the capital of France?"
   The reply greets "Guest": the agent's `before_agent_callback` wrote the
   default `user_name` before the instruction was rendered.
2. Open the State tab: it shows `"user_name": "Guest"`. The State tab is
   read-only; the dev UI cannot set state.
3. A real app sets the name when it creates the session. With `adk web`
   still running, create a session that already has it (the dev UI user id
   is `user`):

   ```bash
   curl -X POST http://localhost:8000/apps/templated_instruction/users/user/sessions \
     -H "Content-Type: application/json" \
     -d '{"session_id": "vishal", "state": {"user_name": "Vishal"}}'
   ```

   Reload the page, pick session `vishal` in the session dropdown, and send
   "What is the capital of France?" again. The callback leaves the existing
   value alone, so the reply greets "Vishal".

## What to look for

- France: both agents usually call the tool. The difference shows at the edges.
- Germany: both agents get `status: error` from `get_capital` (click the
  tool result row in the Events view to see it in the side panel).
  `bad_instruction` then answers "Berlin" from memory,
  because nothing told it not to. `good_instruction` follows its error rule
  and asks you to check the spelling.
- Japan: `bad_instruction` adds a fact list and a follow-up question;
  `good_instruction` keeps to one sentence.
- Templated: the State tab shows `user_name` from the first turn, and the
  reply starts "Hello Guest" (or "Hello Vishal" in the session created with
  `curl`). If nothing sets the key, the optional placeholder resolves to an
  empty string and the run does not fail, because it ends in `?`. A
  required placeholder (`{user_name}`) with no value in state fails the run;
  a `before_agent_callback` default like this one is one way to prevent that.
