# Author: Vishal Bulbule
# Date: 2026-09-22

"""Output keys as glue: the researcher's answer feeds the writer through state.

`output_key="research_findings"` makes ADK save the researcher's final text
into `state["research_findings"]`. The writer's instruction contains the
`{research_findings}` placeholder, which ADK fills from state before the
prompt reaches the model. No tool and no custom code move the data.

The two agents run as a `Workflow` chain, which replaces the deprecated
`SequentialAgent`. In a Workflow the researcher's text is also passed to the
writer as its node input; `output_key` is what makes the value visible in
session state and reusable by any later step.
"""

from google.adk import Workflow
from google.adk.agents import LlmAgent

MODEL = "gemini-3.5-flash"

researcher = LlmAgent(
    model=MODEL,
    name="researcher",
    description="Lists 3 quick facts on the user's topic.",
    instruction=(
        "Give exactly 3 concise factual bullets about the user's topic. "
        "Plain bullets, no preface."
    ),
    output_key="research_findings",
)

writer = LlmAgent(
    model=MODEL,
    name="writer",
    description="Writes a short report from the research findings.",
    instruction=(
        "Write a 2-paragraph report using these findings:\n\n"
        "{research_findings}\n\n"
        "Use a clear, neutral tone. Do not add facts that are not in the "
        "findings."
    ),
    output_key="final_report",
)

root_agent = Workflow(
    name="report_pipeline",
    description="Researcher then writer; output_key carries the data through state.",
    edges=[("START", researcher, writer)],
)
