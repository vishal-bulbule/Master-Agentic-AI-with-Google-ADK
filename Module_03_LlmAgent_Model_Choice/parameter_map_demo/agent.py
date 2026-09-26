# Author: Vishal Bulbule
# Date: 2026-09-22

"""One LlmAgent that sets every commonly used constructor field.

Each field has a short comment explaining what it controls and why this
sample picks the value it does. Read the file top to bottom as a reference
card for `LlmAgent`.

What to notice: `output_key` copies the final reply into session state, and
`generate_content_config` carries sampling settings. On Gemini 3.x models the
thinking tokens count against `max_output_tokens`, so a very small cap can
produce an empty reply.
"""

from google.adk.agents import LlmAgent
from google.genai import types


def get_country_fact(country: str) -> dict:
    """Returns one fun fact about the given country.

    Args:
        country: Country name in English, for example "Japan" or "France".

    Returns:
        A dict with `status` "success" plus `country` and `fact`, or `status`
        "error" with an `error_message` when no fact is stored.
    """
    facts = {
        "japan": "Japan has more than 6,800 islands.",
        "france": "France produces over 1,500 distinct cheeses.",
        "canada": "Canada has the longest coastline of any country.",
        "india": "India is home to the world's largest postal network.",
    }
    fact = facts.get(country.lower())
    if not fact:
        return {"status": "error", "error_message": f"No fact stored for {country}."}
    return {"status": "success", "country": country, "fact": fact}


root_agent = LlmAgent(
    # `model`: which LLM powers this agent. Flash is the default workhorse.
    model="gemini-3.5-flash",

    # `name`: unique ID used by routing, logs, and the `adk web` agent list.
    # Must be a valid Python identifier; avoid reserved names like "user".
    name="country_facts_agent",

    # `description`: other agents read this to decide when to delegate here.
    # Be specific ("country facts only"), not generic ("knows things").
    description="Provides one quick fun fact about a given country.",

    # `instruction`: the system prompt. Answers four questions: who the agent
    # is, what the task is, which tools to use, and what the output looks like.
    instruction=(
        "## Who you are\n"
        "You are a concise country-trivia expert.\n\n"
        "## Task\n"
        "Answer the user with exactly one short fun fact about the country "
        "they mention.\n\n"
        "## Tools\n"
        "Always call `get_country_fact` to look up the fact. Do not invent "
        "facts from memory.\n\n"
        "## Output\n"
        "Reply in a single plain-text sentence. No JSON, no bullet lists.\n"
        "If the tool returns an error, apologize briefly and stop."
    ),

    # `tools`: plain Python functions are wrapped in FunctionTool
    # automatically. The name, docstring, and type hints become the schema.
    tools=[get_country_fact],

    # `output_key`: the agent's final text reply is saved to session state
    # under this key, where later agents, tools, or scripts can read it.
    output_key="last_country_fact",

    # `include_contents`: "default" sends prior conversation turns to the
    # model. "none" makes the agent stateless (useful for classifiers).
    include_contents="default",

    # `generate_content_config`: sampling settings. temperature=0 keeps tool
    # routing repeatable; the output cap leaves room for thinking tokens.
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=1024,
    ),
)
