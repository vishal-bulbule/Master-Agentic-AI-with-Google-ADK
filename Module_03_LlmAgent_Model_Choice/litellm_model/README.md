<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# LiteLLM Model (Claude via Anthropic)

## What this shows

ADK's `LiteLlm` wrapper runs the same `LlmAgent` on a non-Gemini model. Here
the agent uses Claude Haiku 4.5 through the Anthropic API, with a normal
Python function tool. Only the `model` field differs from a Gemini agent.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)). `litellm` is in the
      root `requirements.txt`; if you use your own environment,
      `pip install litellm`.
- [ ] An Anthropic API key from https://console.anthropic.com/, set as
      `ANTHROPIC_API_KEY` in a `.env` at the repository root or in this
      folder (see [`.env.example`](.env.example)). No Google credentials are
      used by this agent.

## Run it

1. `cd Module_03_LlmAgent_Model_Choice`
2. `adk web`
3. Open http://localhost:8000 and select `litellm_model` in the agent dropdown.
4. Send: "What is the capital of Japan?"

Terminal alternative: `adk run litellm_model`.

## What to look for

- Events view: a `get_capital` call and response, then a one-sentence answer
  from Claude.
- The tool schema is built from the function signature and docstring,
  exactly as for Gemini. LiteLLM translates it to the provider's tool format.

## Swapping providers

Change the LiteLLM model string and set the matching key:

| Provider | Model string | Env var |
|---|---|---|
| Anthropic | `anthropic/claude-haiku-4-5` | `ANTHROPIC_API_KEY` |
| OpenAI | `openai/<model-id>` | `OPENAI_API_KEY` |
| Ollama (local) | `ollama_chat/<model-name>` | none (local server) |

ADK also has native Claude classes in `google.adk.models.anthropic_llm`:
`AnthropicLlm` for the Anthropic API and `Claude` for Claude on Agent
Platform. LiteLLM is the choice when you want one code path across many
providers; the trade-off is an extra dependency and a translation layer
between ADK and the provider API.

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| `litellm.AuthenticationError: ... x-api-key header is required` | `ANTHROPIC_API_KEY` missing or empty | Add it to `.env`; the agent also logs a warning at load time when it is unset |
| `ModuleNotFoundError: litellm` | Package not installed | `pip install litellm` |
