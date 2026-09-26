# Author: Vishal Bulbule
# Date: 2026-09-22

"""techtrapture-mcp: the lab server definition, run over stdio.

Defines the whole server surface once:
  Tools     get_course(slug), enroll_student(course_slug, email)
  Resources course://<slug>, one brochure per course
  Prompt    recommend_courses(interests)

Running this file serves it over stdio for MCP Inspector, Claude Desktop, or
a local ADK agent. server_http.py imports the same `mcp` object and serves it
over Streamable HTTP, so the two transports can never drift apart.

Run:
    python server_stdio.py
Inspect:
    npx @modelcontextprotocol/inspector python server_stdio.py
"""

from datetime import datetime, timezone

from fastmcp import FastMCP

from courses import COURSES, ENROLLMENTS, render_course_markdown

mcp = FastMCP("techtrapture-mcp")


@mcp.tool()
def get_course(slug: str) -> dict:
    """Return summary information for a course.

    Args:
        slug: Course slug: adk-bootcamp, mcp-deep-dive, or gemini-prompting.

    Returns:
        A dict with status and the course fields, or status "error" and the
        list of available slugs.
    """
    course = COURSES.get(slug)
    if not course:
        return {
            "status": "error",
            "error": f"course '{slug}' not found",
            "available": list(COURSES),
        }
    return {"status": "success", "slug": slug, **course}


@mcp.tool()
def enroll_student(course_slug: str, email: str) -> dict:
    """Enroll a learner in a course.

    Args:
        course_slug: Slug of the course, as returned by get_course.
        email: Learner's email address.

    Returns:
        A dict with status and the enrollment_id, course_slug, email, and
        enrolled_at timestamp, or status "error" and a message.
    """
    if course_slug not in COURSES:
        return {"status": "error", "error": f"course '{course_slug}' not found"}
    if "@" not in email or "." not in email.split("@")[-1]:
        return {"status": "error", "error": f"invalid email: {email!r}"}

    enrollment = {
        "enrollment_id": f"E-{len(ENROLLMENTS) + 1001}",
        "course_slug": course_slug,
        "email": email.lower(),
        "enrolled_at": datetime.now(timezone.utc).isoformat(),
    }
    ENROLLMENTS.append(enrollment)
    return {"status": "success", **enrollment}


def _register_brochure(slug: str) -> None:
    @mcp.resource(
        f"course://{slug}",
        name=f"{slug}-brochure",
        description=f"Brochure for the {COURSES[slug]['title']} course, as markdown.",
        mime_type="text/markdown",
    )
    def read_course() -> str:
        return render_course_markdown(slug)


# One concrete resource per course rather than a `course://{slug}` template:
# templates are not returned by resources/list, and clients such as ADK's
# load_mcp_resource tool can only read resources that are listed.
for _slug in COURSES:
    _register_brochure(_slug)


@mcp.prompt()
def recommend_courses(interests: str) -> str:
    """Turn free-text interests into a course recommendation prompt."""
    catalog_lines = "\n".join(
        f"- {slug}: {c['title']} ({c['level']}, {c['duration_hours']}h, "
        f"INR {c['price_inr']:,}). {c['summary']}"
        for slug, c in COURSES.items()
    )
    return (
        "You are a course advisor. Recommend 1 or 2 courses for a learner "
        f"whose interests are: {interests}\n\n"
        f"Catalog:\n{catalog_lines}\n\n"
        "Reply with:\n"
        "1. The chosen course slug(s).\n"
        "2. A two-sentence reason per slug.\n"
        "3. An invitation to ask follow-up questions."
    )


if __name__ == "__main__":
    mcp.run()
