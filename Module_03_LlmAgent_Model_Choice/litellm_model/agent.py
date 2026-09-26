# Author: Vishal Bulbule
# Date: 2026-09-22

"""Run an LlmAgent on Claude through the LiteLLM wrapper.

`LiteLlm(model="<provider>/<model_id>")` lets `LlmAgent` use any provider
LiteLLM supports (Anthropic, OpenAI, Mistral, local Ollama, vLLM, and more).
Everything else stays the same: the constructor, tool registration, and how
`adk web` or `adk run` loads the agent. Only the `model` field changes.

This sample needs `litellm` installed and `ANTHROPIC_API_KEY` set. No Google
credentials are used.
"""

import logging
import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Warn at load time; otherwise the first sign of a missing key is an
# authentication error in the middle of a run.
if not os.environ.get("ANTHROPIC_API_KEY"):
    logging.getLogger(__name__).warning(
        "ANTHROPIC_API_KEY is not set. Add it to .env before running this agent."
    )


def get_capital(country: str) -> dict:
    """Returns the capital city for a given country.

    Args:
        country: Country name in English, for example "Japan".

    Returns:
        A dict with `status` "success" plus `country` and `capital`, or
        `status` "error" with an `error_message` for an unknown country.
    """
    capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
    capital = capitals.get(country.lower())
    if not capital:
        return {"status": "error", "error_message": f"Unknown country: {country}"}
    return {"status": "success", "country": country, "capital": capital}


# LiteLLM model strings follow `<provider>/<model_id>`. Haiku is the cheapest
# current Claude model; swap in `anthropic/claude-sonnet-5` or
# `anthropic/claude-opus-5` for harder tasks.
CLAUDE_MODEL_ID = "anthropic/claude-haiku-4-5"

root_agent = LlmAgent(
    model=LiteLlm(model=CLAUDE_MODEL_ID),
    name="claude_capital_agent",
    description="Capital-city helper powered by Anthropic Claude via LiteLLM.",
    instruction=(
        "You are a concise capital-city expert. For every country question, "
        "call `get_capital` and reply with a single short sentence."
    ),
    tools=[get_capital],
)
