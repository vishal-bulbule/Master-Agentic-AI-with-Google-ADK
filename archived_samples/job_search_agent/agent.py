from google.adk.agents import LlmAgent, SequentialAgent

GEMINI_MODEL = "gemini-2.5-flash"

# --- 1. Open Job Positions Agent ---
open_positions_agent = LlmAgent(
    name="OpenPositionsAgent",
    model=GEMINI_MODEL,
    instruction="""
You are a Job search assistant. Based on the user query do your research on web and,
list 5  open job positions.

For each position include:
- Job Title
- Company
- Location

Output as a numbered list.
""",
    output_key="open_positions"
)

# --- 2. Interview Q&A Agent ---
interview_qa_agent = LlmAgent(
    name="InterviewQAAgent",
    model=GEMINI_MODEL,
    instruction="""
You are an interview coach. For the given query and referring to {open_positions},
create 5 common interview questions with strong sample answers.

Format:
Q: <question>
A: <answer>
""",
    output_key="interview_qa"
)

# --- 3. Interview Tips & Tricks Agent ---
interview_tips_agent = LlmAgent(
    name="InterviewTipsAgent",
    model=GEMINI_MODEL,
    instruction="""
You are a career mentor. Provide practical tips & tricks to excel in interviews in 200 words
for the user query. Use {open_positions} to tailor your advice. ALso advise on {interview_qa}.

Cover:
- How to research the company
- What to prepare technically
- Behavioral interview strategies
- Body language & communication tips

Output as a bulleted list.
""",
    output_key="interview_tips"
)

# --- Combine into Sequential LLM Pipeline ---
interview_prep_pipeline = SequentialAgent(
    name="InterviewPrepPipeline",
    sub_agents=[open_positions_agent, interview_qa_agent, interview_tips_agent],
    description="Suggests open jobs, interview Q&A, and preparation tips"
)

# Root agent
root_agent = interview_prep_pipeline
