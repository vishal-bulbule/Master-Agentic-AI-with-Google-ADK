# Author: Vishal Bulbule
# Date: 2026-09-22

"""Save and load a PDF as a versioned artifact.

State is for small JSON values. Binary files belong in artifacts:
`tool_context.save_artifact(filename, part)` stores a `types.Part` holding the
bytes and returns a version number (0, 1, 2, ... per filename), and
`tool_context.load_artifact(filename)` returns the latest version. The bytes
never enter the model's context; the model only sees the tool results.

The PDF is generated in code with the standard library, so the sample needs
no extra packages and the model never has to copy file contents.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from google.genai import types


def _build_pdf(title: str, body: str) -> bytes:
    """Build a one-page PDF with a title line and a body line."""

    def escape(text: str) -> str:
        text = text.encode("latin-1", "replace").decode("latin-1")
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    stream = (
        f"BT /F1 18 Tf 72 720 Td ({escape(title)}) Tj ET\n"
        f"BT /F1 12 Tf 72 690 Td ({escape(body)}) Tj ET\n"
    ).encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = b"%PDF-1.4\n"
    offsets = []
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += b"%d 0 obj\n" % number + obj + b"\nendobj\n"
    xref_start = len(pdf)
    pdf += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    pdf += b"".join(b"%010d 00000 n \n" % offset for offset in offsets)
    pdf += b"trailer\n<< /Size %d /Root 1 0 R >>\n" % (len(objects) + 1)
    pdf += b"startxref\n%d\n%%%%EOF\n" % xref_start
    return pdf


async def save_pdf_report(
    filename: str, title: str, body: str, tool_context: ToolContext
) -> dict:
    """Generate a one-page PDF and save it as a versioned artifact.

    Args:
        filename: The artifact filename, for example "report.pdf".
        title: The heading printed at the top of the page.
        body: One line of text printed under the heading.
        tool_context: Injected by ADK; gives the tool access to artifacts.

    Returns:
        A dict with status, filename, the saved version, and the size in bytes.
    """
    pdf_bytes = _build_pdf(title, body)
    part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
    version = await tool_context.save_artifact(filename, part)
    return {
        "status": "ok",
        "filename": filename,
        "version": version,
        "bytes": len(pdf_bytes),
    }


async def load_pdf_artifact(filename: str, tool_context: ToolContext) -> dict:
    """Load the latest version of a saved artifact and report its size and type.

    Args:
        filename: The artifact filename to load.
        tool_context: Injected by ADK; gives the tool access to artifacts.

    Returns:
        A dict with status, filename, size in bytes, and MIME type, or status
        "not_found" if no artifact has that name.
    """
    part = await tool_context.load_artifact(filename)
    if part is None or part.inline_data is None:
        return {"status": "not_found", "filename": filename}
    return {
        "status": "ok",
        "filename": filename,
        "bytes": len(part.inline_data.data or b""),
        "mime_type": part.inline_data.mime_type,
    }


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="artifact_pdf_agent",
    description="Creates, saves, and loads PDF artifacts.",
    instruction=(
        "You manage PDF artifacts. When the user asks for a PDF, call "
        "save_pdf_report(filename, title, body); pick a short title and a "
        "one-sentence body from their request if they do not give one. When "
        "they ask to load a file back, call load_pdf_artifact(filename). "
        "Summarize each tool result in one short sentence, including the "
        "version number after a save."
    ),
    tools=[save_pdf_report, load_pdf_artifact],
)
