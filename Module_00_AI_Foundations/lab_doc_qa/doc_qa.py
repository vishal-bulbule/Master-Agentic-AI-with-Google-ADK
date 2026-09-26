# Author: Vishal Bulbule
# Date: 2026-09-22

"""Doc-grounded Q&A from the command line, with no framework.

The flow:
  1. Take the question from the command line.
  2. Fetch grounding context with `search_docs()`.
  3. Put the chunks into the prompt and tell the model to answer only from them.
  4. Stream the answer.
  5. Print input and output tokens and an estimated cost.

`search_docs()` is a stub with three hardcoded snippets so the script runs as
is. Replace its body with a call to a documentation MCP server, using the
client pattern in ../09_mcp_grounding/mcp_grounding.py. It is async so that
swap needs no other changes.

Run:
    python doc_qa.py "How do I install ADK?"
"""

import asyncio
import sys
from typing import Iterable

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

# Example rates in USD per 1M tokens. Replace with the current published rates.
INPUT_USD_PER_M = 0.30
OUTPUT_USD_PER_M = 2.50


async def search_docs(query: str) -> list[str]:
    """Stub retrieval. Replace with a real MCP search call."""
    return [
        "ADK installation (Python): `pip install google-adk`. Requires Python 3.10+.",
        "Cloud Run cold starts: First request after scale-to-zero pays ~1-3s to "
        "start the container. Set --min-instances=1 to avoid.",
        "Cloud Function with Secret Manager: bind the secret to an env var via "
        "`--set-secrets=API_KEY=API_KEY:latest`.",
    ]


def build_grounded_prompt(question: str, chunks: Iterable[str]) -> str:
    joined = "\n\n".join(f"<doc>\n{c}\n</doc>" for c in chunks)
    return (
        "You are a documentation assistant. Answer ONLY from the docs below. "
        "If the answer isn't there, say so. Cite which <doc> you used.\n\n"
        f"{joined}\n\nQuestion: {question}"
    )


async def answer(question: str) -> None:
    chunks = await search_docs(question)
    prompt = build_grounded_prompt(question, chunks)

    total_in = 0
    total_out = 0

    print(f"\nQ: {question}\nA: ", end="", flush=True)
    for chunk in client.models.generate_content_stream(
        model="gemini-3.5-flash",
        contents=prompt,
    ):
        print(chunk.text or "", end="", flush=True)
        # Usage arrives on the last chunks; thinking tokens are billed as output.
        if m := chunk.usage_metadata:
            total_in = m.prompt_token_count or total_in
            total_out = (m.candidates_token_count or 0) + (m.thoughts_token_count or 0) or total_out

    cost = (total_in * INPUT_USD_PER_M + total_out * OUTPUT_USD_PER_M) / 1_000_000
    print(f"\n\n[tokens in={total_in} out={total_out} (incl. thinking) cost ~${cost:.6f}]")


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "How do I install ADK in Python?"
    asyncio.run(answer(q))
