# Author: Vishal Bulbule
# Date: 2026-09-22

"""BROKEN on purpose: the tool function has no docstring.

ADK sends the docstring to the model as the tool's description. Without it the
model only has the function name and parameter names to go on. A name as clear
as `get_capital` hides the problem; vague or overlapping tool names do not.
See FIX.md.
"""

from google.adk.agents import LlmAgent


# WRONG: no docstring, so the tool declaration has no description.
def get_capital(country: str) -> dict:
    capitals = {"france": "Paris", "japan": "Tokyo", "india": "New Delhi"}
    return {
        "status": "success",
        "capital": capitals.get(country.lower(), "Unknown"),
    }


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="broken_no_docstring",
    description="Demonstrates the missing-docstring failure.",
    instruction="Use the available tools to answer questions about capitals.",
    tools=[get_capital],
)
