<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Fix: credentials never reach the process

## Reproduce

`adk web` and `adk run` look for a `.env` in the agent folder and then in each
parent folder, and load the first one they find. With a `.env` at the
repository root this agent simply works. To see the failure you get when no
`.env` is found, turn that lookup off, in a shell that has no Google
credentials exported:

```bash
cd Module_02_First_ADK_Agent/common_failures
ADK_DISABLE_LOAD_DOTENV=1 adk run broken_no_env "Are you up?"
```

## Symptom

The agent loads fine, and the first model call fails:

```
Error: No API key was provided. Please pass a valid API key. Learn how to create an API key at https://ai.google.dev/gemini-api/docs/api-key.
```

In `adk web` the agent appears in the list and the error shows up when you
send the first message. If your key is present but wrong you get
`400 API key not valid` instead; with Agent Platform settings but no
`gcloud auth application-default login`, a `DefaultCredentialsError`.

## Why

ADK reads credentials from environment variables: `GOOGLE_API_KEY` for the
Gemini API, or `GOOGLE_GENAI_USE_ENTERPRISE=TRUE` plus `GOOGLE_CLOUD_PROJECT`
and `GOOGLE_CLOUD_LOCATION` for Agent Platform (formerly Vertex AI). A `.env`
file only helps if it is loaded. That fails when:

- the `.env` is not in the agent folder or any parent of it (for example it
  sits in a sibling folder, or next to where you ran `pip install`);
- the file is named `.env.example`, `env` or `.env.txt`;
- `ADK_DISABLE_LOAD_DOTENV` is set, as some deployment setups do;
- the agent runs through your own Python script, which does not load `.env`
  unless you call `load_dotenv()` yourself.

A `.env` in an agent folder replaces the root one; the two are not merged, so
a partial per-agent `.env` can also hide the root credentials.

## Fix

Put the `.env` where ADK looks: at the repository root (see
[SETUP.md](../../../SETUP.md)) or in the agent folder. Start from the
`.env.example` in the agent folder. To check which file was loaded, open the
log file whose path `adk run` prints at startup and look for
`Loaded .env file for <agent> at <path>` or `No .env file found for <agent>`.

For your own scripts that build a `Runner` directly, call `load_dotenv()`
(from `python-dotenv`) before the first model call.

Exporting the variables in your shell also works, and exported values take
precedence over `.env` values:

```bash
export GOOGLE_API_KEY="your-key"
adk web
```

That lasts only for the current terminal, which is why a `.env` file is the
usual choice.
