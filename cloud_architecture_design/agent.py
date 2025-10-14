
import asyncio
import os
from google.adk.agents import LoopAgent, LlmAgent, BaseAgent, SequentialAgent
from google.genai import types
from google.adk.runners import InMemoryRunner
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools.tool_context import ToolContext
from typing import AsyncGenerator, Optional
from google.adk.events import Event, EventActions


GEMINI_MODEL = "gemini-2.0-flash"
#STATE_INITIAL_TOPIC = "initial_topic"

# --- State Keys ---
STATE_CURRENT_DOC = "current_document"
STATE_CRITICISM = "criticism"
# Define the exact phrase the Critic should use to signal completion
COMPLETION_PHRASE = "No major issues found."

# --- Tool Definition ---
def exit_loop(tool_context: ToolContext):
  """Call this function ONLY when the critique indicates no further changes are needed, signaling the iterative process should end."""
  print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
  tool_context.actions.escalate = True
  # Return empty dict as tools should typically return JSON-serializable output
  return {}

# --- Agent Definitions ---

# STEP 1: Initial Writer Agent (Runs ONCE at the beginning)
initial_writer_agent = LlmAgent(
    name="InitialWriterAgent",
    model=GEMINI_MODEL,
    include_contents='none',
    # MODIFIED Instruction: Ask for a slightly more developed start
    instruction=f"""You are a cloud architect. Based ONLY on the user's requirements ,
draft an initial cloud architecture..
Output must include:
- Key components & services
- Deployment topology (regions, zones, network layout)
- Security considerations
- Cost levers (main drivers)
- HA/Resilience notes

Output ONLY the design text, no explanations.
""",
    description="Generates initial draft of cloud architecture",
    output_key=STATE_CURRENT_DOC
)

# STEP 2a: Critic Agent (Inside the Refinement Loop)
critic_agent_in_loop = LlmAgent(
    name="CriticAgent",
    model=GEMINI_MODEL,
    include_contents='none',
    # MODIFIED Instruction: More nuanced completion criteria, look for clear improvement paths.
    instruction=f"""You are a senior cloud reviewer. Review the given design.

    **Document to Review:**
    ```
    {STATE_CURRENT_DOC}
    ```

    **Task:**  
Evaluate the proposed architecture for only using Google Cloud services. Identify any potential issues, gaps, or areas for improvement.:
- Best practices  
- Security  
- Cost efficiency  
- High availability  

Rules for response:  
1. If you find 1–3 clear issues, list them briefly as critique points.  
2. If the design is sound, coherent, addresses the topic adequately for its scope, and has no glaring errors or omissions,  
   respond *exactly* with the phrase "{COMPLETION_PHRASE}" and nothing else.  
3. Do not suggest purely subjective or stylistic preferences if the architecture is functionally complete.  
""",
    description="Reviews the architecture design.",
    output_key=STATE_CRITICISM
)


# STEP 2b: Refiner/Exiter Agent (Inside the Refinement Loop)
refiner_agent_in_loop = LlmAgent(
    name="RefinerAgent",
    model=GEMINI_MODEL,
    # Relies solely on state via placeholders
    include_contents='none',
    instruction=f"""You are a Senior Cloud Architect refining a document based on feedback OR exiting the process.
    **Current Document:**
    ```
    {STATE_CURRENT_DOC}
    ```
    **Critique/Suggestions:**
    ```
    {STATE_CRITICISM}
    ```
   
**Task:**  
- If critique == "{COMPLETION_PHRASE}":  
  Call the exit_loop tool (do not output any text).  

- Else:  
  Carefully apply the critique suggestions to improve the 'Current Document'.  
  The refined design must include:  
  - Key components & services  
  - Deployment topology (regions, zones, network layout)  
  - Security considerations  
  - Cost levers (main drivers)  
  - HA/Resilience notes  

**Important:**  
- Output *only* the refined document text.  
- Do not add explanations, commentary, or extra text.  
- Either output the refined document OR call the exit_loop function.  
""",
    description="Refines the design based on critique or exits loop.",
    tools=[exit_loop], # Provide the exit_loop tool
    output_key=STATE_CURRENT_DOC # Overwrites state['current_document'] with the refined version
)


# STEP 2: Refinement Loop Agent
refinement_loop = LoopAgent(
    name="RefinementLoop",
    # Agent order is crucial: Critique first, then Refine/Exit
    sub_agents=[
        critic_agent_in_loop,
        refiner_agent_in_loop,
    ],
    max_iterations=5 # Limit loops
)

# STEP 3: Overall Sequential Pipeline
# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = SequentialAgent(
    name="IterativeWritingPipeline",
    sub_agents=[
        initial_writer_agent, # Run first to create initial doc
        refinement_loop       # Then run the critique/refine loop
    ],
    description="Iteratively generates and refines a cloud architecture until stable."
)