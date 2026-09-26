# Author: Vishal Bulbule
# Date: 2026-09-22

"""Sequential code pipeline: code_writer, then code_reviewer, then code_refactorer.

A `Workflow` with a single chain of edges runs its nodes in a fixed order. This
is the ADK 2.x replacement for the deprecated `SequentialAgent`.

Two channels carry data between the steps. Each agent's text answer becomes
the next node's input, and each agent's `output_key` also writes that answer
into session state, where later instructions read it with `{key}`
placeholders. The refactorer needs both the code and the review, so it reads
them from state rather than relying on its node input alone.
"""

from google.adk import Workflow
from google.adk.agents import LlmAgent

MODEL = "gemini-3.5-flash"

code_writer = LlmAgent(
    model=MODEL,
    name="code_writer",
    description="Writes an initial Python implementation for the user's request.",
    instruction=(
        "You are a senior Python engineer. Given the user's request, write a "
        "small, working Python function with a short docstring. Respond with "
        "only the code block, no commentary."
    ),
    output_key="generated_code",
)

code_reviewer = LlmAgent(
    model=MODEL,
    name="code_reviewer",
    description="Reviews the generated code and lists concrete issues.",
    instruction=(
        "You are a strict code reviewer. Review the following code:\n\n"
        "```python\n{generated_code}\n```\n\n"
        "List concrete issues: correctness bugs, edge cases, style, "
        "performance. If the code is fine, say so. Use 3-6 short bullets."
    ),
    output_key="review_comments",
)

code_refactorer = LlmAgent(
    model=MODEL,
    name="code_refactorer",
    description="Refactors the code applying the reviewer's comments.",
    instruction=(
        "You are a refactoring expert. Apply the reviewer's feedback to the "
        "code.\n\n"
        "Original code:\n```python\n{generated_code}\n```\n\n"
        "Review:\n{review_comments}\n\n"
        "Respond with only the final refactored code block."
    ),
    output_key="final_code",
)

root_agent = Workflow(
    name="code_pipeline",
    description="Writes, reviews, and refactors Python code in three fixed steps.",
    edges=[("START", code_writer, code_reviewer, code_refactorer)],
)
