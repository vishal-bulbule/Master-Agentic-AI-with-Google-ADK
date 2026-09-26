# Author: Vishal Bulbule
# Date: 2026-09-22

"""A multi-agent hierarchy: one LlmAgent coordinator with three sub-agents.

    assistant_team_root (LlmAgent)
      |-- researcher     (LlmAgent)
      |-- code_pipeline  (SequentialAgent)
      |     |-- code_writer
      |     |-- code_reviewer
      |     |-- code_refactorer
      |-- critic         (LlmAgent)

The coordinator picks a sub-agent from their `description` fields and hands
over with `transfer_to_agent`. A sub-agent can be any agent, including a
workflow of its own; the coordinator only sees its name and description.

`code_pipeline` stays a `SequentialAgent` on purpose. `SequentialAgent` is
deprecated in ADK 2.x in favor of `Workflow`, but a `Workflow` cannot yet be
an `LlmAgent` sub-agent, so this is the one place the older class is still
needed.
"""

from google.adk.agents import LlmAgent, SequentialAgent

MODEL = "gemini-3.5-flash"


researcher = LlmAgent(
    model=MODEL,
    name="researcher",
    description="Answers factual questions with concise, sourced answers.",
    instruction=(
        "You are a research assistant. Answer the user's factual question in "
        "2-4 sentences. If you don't know, say so."
    ),
)


code_writer = LlmAgent(
    model=MODEL,
    name="code_writer",
    description="Writes initial Python code for a task.",
    instruction="Write a small Python function. Output ONLY the code.",
    output_key="generated_code",
)

code_reviewer = LlmAgent(
    model=MODEL,
    name="code_reviewer",
    description="Reviews code for bugs and style.",
    instruction=(
        "Review this code in 3 bullets:\n```python\n{generated_code}\n```"
    ),
    output_key="review_comments",
)

code_refactorer = LlmAgent(
    model=MODEL,
    name="code_refactorer",
    description="Applies review feedback to produce the final code.",
    instruction=(
        "Apply the review to the code.\n\n"
        "Code:\n```python\n{generated_code}\n```\n\n"
        "Review:\n{review_comments}\n\n"
        "Output ONLY the final refactored code."
    ),
    output_key="final_code",
)

code_pipeline = SequentialAgent(
    name="code_pipeline",
    description="Three-step Python coding pipeline: writes, reviews, refactors.",
    sub_agents=[code_writer, code_reviewer, code_refactorer],
)


critic = LlmAgent(
    model=MODEL,
    name="critic",
    description="Evaluates a piece of writing and points out issues.",
    instruction=(
        "You are a strict literary critic. Given a piece of writing from the "
        "user, give 3 short bullets covering: clarity, style, and one "
        "concrete suggestion."
    ),
)


root_agent = LlmAgent(
    model=MODEL,
    name="assistant_team_root",
    description="Routes user requests to a researcher, code pipeline, or critic.",
    instruction=(
        "You coordinate a small team of specialists. Choose the best one for "
        "the user's request and delegate:\n"
        "  - researcher: factual questions, general knowledge, who/what/when\n"
        "  - code_pipeline: any request to write, review, or refactor code\n"
        "  - critic: any request to evaluate or critique a piece of writing\n"
        "Delegate via transfer_to_agent. Do not answer yourself."
    ),
    sub_agents=[researcher, code_pipeline, critic],
)
