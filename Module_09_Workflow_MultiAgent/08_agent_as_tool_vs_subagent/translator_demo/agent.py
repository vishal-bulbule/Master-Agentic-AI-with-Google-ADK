# Author: Vishal Bulbule
# Date: 2026-09-22

"""Agent as a tool: the concierge calls a translator and keeps the conversation.

The translator is wrapped in `AgentTool` and passed in `tools`. The concierge
calls it like a function, gets the English text back as the tool result, and
then writes the reply itself. The translator never talks to the user.
Compare with `support_team`, where the specialist takes over the conversation.
"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

MODEL = "gemini-3.5-flash"


translator = LlmAgent(
    model=MODEL,
    name="translator",
    description="Translates the input text to English.",
    instruction=(
        "You translate the input text to clear, neutral English. Output only "
        "the translation, with no commentary and no quotes."
    ),
)


translate_tool = AgentTool(agent=translator)


root_agent = LlmAgent(
    model=MODEL,
    name="concierge",
    description="A friendly multilingual concierge that uses a translator tool.",
    instruction=(
        "You are a friendly hotel concierge. When the user writes in a "
        "language other than English, call the 'translator' tool with their "
        "text to get an English version, then craft a warm reply in English "
        "(and reflect their language briefly at the end if you can). Do not "
        "invent specific business names; ask about preferences instead.\n"
        "If the user already writes in English, just reply normally without "
        "calling the tool."
    ),
    tools=[translate_tool],
)
