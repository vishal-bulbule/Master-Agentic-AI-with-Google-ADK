# Author: Vishal Bulbule
# Date: 2026-09-22

"""Agent Skills with SkillToolset: load instructions only when needed.

A skill is a folder with a SKILL.md file (name, description, instructions)
and optional references/, assets/, and scripts/. SkillToolset gives the agent
tools to discover skills and load them on demand:

- The model first sees only each skill's name and description.
- It calls load_skill to read a skill's instructions when a request needs it.
- It calls load_skill_resource to read files such as references/glossary.md.

This keeps unused instructions out of the context window. The sample has one
skill loaded from disk and one defined in code. Skills are experimental in
ADK, so expect a warning on startup.
"""

import pathlib

from google.adk.agents import LlmAgent
from google.adk.skills import Frontmatter, Skill, load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset

SKILLS_DIR = pathlib.Path(__file__).parent / "skills"

translate_skill = load_skill_from_dir(SKILLS_DIR / "translate-to-french")

meeting_summary_skill = Skill(
    frontmatter=Frontmatter(
        name="meeting-summary",
        description=(
            "Turns raw meeting notes into a short summary with decisions and "
            "action items. Use when the user pastes meeting notes."
        ),
    ),
    instructions=(
        "Write three sections: Summary (two sentences), Decisions (bullets), "
        "and Action items (bullets in the form 'owner: task, due date'). "
        "Write 'none' for an empty section. Do not invent owners or dates."
    ),
)

root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="skills_demo_agent",
    description="Assistant that loads packaged skills on demand.",
    instruction=(
        "You are a helpful assistant. When a request matches one of your "
        "skills, load that skill and follow its instructions."
    ),
    tools=[SkillToolset(skills=[translate_skill, meeting_summary_skill])],
)
