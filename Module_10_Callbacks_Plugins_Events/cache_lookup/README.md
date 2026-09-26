<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Response cache

## What this shows

A `before_model_callback` and an `after_model_callback` working as a pair. The
first hashes the latest user message and, on a cache hit, returns an
`LlmResponse` so the model call is skipped. On a miss it saves the key in
`temp:` state and lets the call go ahead; the second stores the model's answer
under that key. `temp:` state lives for one invocation and is not saved to the
session, which makes it the right place to pass a value from a `before_*`
callback to its `after_*` partner. With streaming on, `after_model` also sees
each partial chunk, so the store step skips partial responses.

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Credentials go in a `.env` at the repository root or in the agent folder; `.env.example` in this folder lists the variables (a Gemini API key, or Agent Platform (formerly Vertex AI) with `gemini-3.5-flash` on location `global`).

## Run it

1. `cd Module_10_Callbacks_Plugins_Events`
2. `adk web`
3. Open http://localhost:8000 and select `cache_lookup` in the agent dropdown.
4. Send: `What is 2 + 2?`

The callbacks print to the terminal where `adk web` is running; keep it visible.
Terminal alternative: `adk run cache_lookup` prints the same lines inline with the chat.

## Try it

Send the same question twice in one session: `What is 2 + 2?`

## What to look for

```
[cache] MISS key=692a9daa, calling model
[cache] STORE key=692a9daa (chars=21)
[cache] HIT  key=692a9daa, model call skipped
```

- The second answer arrives instantly and uses no tokens; the Traces view
  shows no model call for it.
- The key is the latest user message only, lowercased. Hashing the whole
  `llm_request.contents` would never hit within a session, because the history
  is different on every turn.
- Keying on the question alone ignores context: "and in French?" after two
  different questions returns the same cached answer. Real caches key on
  whatever makes the answer unique for your workload.
- The dict lives in the process and never expires. Restarting `adk web` clears
  it. Use Memorystore (Redis) with a TTL when more than one instance serves
  traffic.

## Clean up

`adk web` and `adk run` keep sessions in `cache_lookup/.adk/session.db`. Delete it to start clean: `rm -rf cache_lookup/.adk`
