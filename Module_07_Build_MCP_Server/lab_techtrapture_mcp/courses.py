# Author: Vishal Bulbule
# Date: 2026-09-22

"""In-memory course catalog shared by the lab servers.

A production server would read this from Firestore or Cloud SQL. A dict keeps
the lab self-contained. The catalog is sample data.
"""

COURSES = {
    "adk-bootcamp": {
        "title": "ADK Bootcamp",
        "author": "Vishal Bulbule",
        "duration_hours": 16,
        "price_inr": 4999,
        "level": "Beginner",
        "topics": ["LlmAgent", "Tools", "Sessions", "Workflows"],
        "summary": (
            "Hands-on introduction to Google's Agent Development Kit. "
            "Build an agent, add custom tools, and deploy it to Cloud Run."
        ),
    },
    "mcp-deep-dive": {
        "title": "MCP Deep Dive",
        "author": "Vishal Bulbule",
        "duration_hours": 12,
        "price_inr": 3999,
        "level": "Intermediate",
        "topics": ["FastMCP", "Tools", "Resources", "Prompts", "Streamable HTTP"],
        "summary": (
            "From protocol fundamentals to building and shipping your own "
            "MCP servers on Cloud Run."
        ),
    },
    "gemini-prompting": {
        "title": "Gemini Prompting Patterns",
        "author": "Vishal Bulbule",
        "duration_hours": 6,
        "price_inr": 1999,
        "level": "Beginner",
        "topics": ["Prompting", "Long Context", "Multimodal"],
        "summary": (
            "Practical prompting patterns for Gemini: instruction stacking, "
            "role priming, structured output."
        ),
    },
}

# Enrollments made through enroll_student, kept for the life of the process.
ENROLLMENTS: list[dict] = []


def render_course_markdown(slug: str) -> str:
    """Format one course as markdown for the course:// resource."""
    course = COURSES.get(slug)
    if not course:
        return f"# Course `{slug}`\n\n_Not found._"
    topics = "\n".join(f"- {t}" for t in course["topics"])
    return (
        f"# {course['title']}\n\n"
        f"**Author:** {course['author']}  \n"
        f"**Duration:** {course['duration_hours']} hours  \n"
        f"**Level:** {course['level']}  \n"
        f"**Price:** INR {course['price_inr']:,}\n\n"
        f"## Summary\n{course['summary']}\n\n"
        f"## Topics\n{topics}\n"
    )
