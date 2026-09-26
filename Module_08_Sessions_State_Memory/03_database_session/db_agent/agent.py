# Author: Vishal Bulbule
# Date: 2026-09-22

"""Note-taking agent used with DatabaseSessionService.

The agent appends notes to a list in session state. When `adk web` runs with
`--session_service_uri=sqlite+aiosqlite:///./sessions.db`, ADK stores sessions
in SQLite through `DatabaseSessionService`, so the notes and the full event
history survive a server restart.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext


def add_note(text: str, tool_context: ToolContext) -> dict:
    """Append a note to the session's notes list.

    Args:
        text: A short note to remember in this session.
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status and the number of stored notes.
    """
    notes = list(tool_context.state.get("notes", []))
    notes.append(text)
    tool_context.state["notes"] = notes
    return {"status": "ok", "count": len(notes)}


def list_notes(tool_context: ToolContext) -> dict:
    """Return all notes stored in session state.

    Args:
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status, the note count, and the notes.
    """
    notes = list(tool_context.state.get("notes", []))
    return {"status": "ok", "count": len(notes), "notes": notes}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="db_notes_agent",
    description="Stores notes in a persisted session.",
    instruction=(
        "You are a note-taking assistant. When the user gives you something "
        "to remember, call add_note(text). When they ask what they have "
        "noted, call list_notes()."
    ),
    tools=[add_note, list_notes],
)
