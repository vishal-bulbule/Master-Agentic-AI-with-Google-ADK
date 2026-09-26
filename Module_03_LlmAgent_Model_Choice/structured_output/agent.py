# Author: Vishal Bulbule
# Date: 2026-09-22

"""Structured output: the final reply must match a Pydantic schema.

Pass a Pydantic model as `output_schema` and the model is constrained to emit
JSON that matches it. ADK validates the reply, and because `output_key` is
also set, stores the parsed result (a dict) in session state under
`found_capital`, where the `adk web` State tab shows it.

This agent has no tools, so the example stays focused on the schema. Current
ADK versions also accept `output_schema` together with `tools`: tools run
during the reasoning loop and the schema is enforced on the final answer only.
"""

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field


class CapitalOutput(BaseModel):
    """Schema the agent's final response must match."""

    country: str = Field(description="The country the user asked about.")
    capital: str = Field(description="The capital city of that country.")
    confidence: float = Field(
        description="Model self-rated confidence, 0.0 to 1.0.",
        ge=0.0,
        le=1.0,
    )


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="structured_capital_agent",
    description="Returns capital city info as strict JSON (no prose).",
    instruction=(
        "You are a capital-city lookup service. Given a user question, "
        "respond ONLY with a JSON object that matches the CapitalOutput "
        "schema: {country, capital, confidence}. "
        "Use 0.95 for capitals you are very sure of, 0.6 for uncertain ones. "
        "Do not include any prose, markdown, or code fences."
    ),
    output_schema=CapitalOutput,
    output_key="found_capital",
)
