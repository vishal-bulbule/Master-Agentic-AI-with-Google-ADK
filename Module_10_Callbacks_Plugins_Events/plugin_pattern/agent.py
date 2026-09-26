# Author: Vishal Bulbule
# Date: 2026-09-22

"""An agent protected by GuardrailPlugin, registered through an App.

Plugins are registered on the App, not on the agent. `adk run` and `adk web`
look for a module-level `app` first and fall back to `root_agent`, so exposing
`app` here is all it takes for the plugin to be active in both.

The agent itself has no callbacks. All guardrail behavior comes from the
plugin, which could cover any number of agents in the same App.
"""

from google.adk.agents import LlmAgent
from google.adk.apps import App

from .guardrail_plugin import GuardrailPlugin

root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="guardrail_plugin_agent",
    description="Customer-service agent protected by GuardrailPlugin.",
    instruction=(
        "You are a customer-service assistant. Be concise and polite. If the "
        "user asks you to quote or repeat words, do so exactly."
    ),
)

# adk web lists apps by folder name; keeping the App name the same avoids two
# names for one app. App names must start with a letter.
app = App(
    name="plugin_pattern",
    root_agent=root_agent,
    plugins=[GuardrailPlugin(token_budget=10_000)],
)
