# Author: Vishal Bulbule
# Date: 2026-09-22

"""Greeter whose instruction reads `{user_name?}` from session state.

ADK replaces `{key}` placeholders in an instruction with state values before
the prompt is sent. The `?` suffix makes the key optional: when it is missing
the placeholder becomes an empty string instead of raising an error. No tool
call is needed to personalize the reply.
"""

from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="greeter_agent",
    description="Greets the user by name when state['user_name'] is set.",
    instruction=(
        "You are a friendly greeter. The user's name is {user_name?}. "
        "If you know the name, greet the user by name. If not, just say hi."
    ),
)
