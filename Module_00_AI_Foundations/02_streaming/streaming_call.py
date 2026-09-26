# Author: Vishal Bulbule
# Date: 2026-09-22

"""Stream a Gemini response chunk by chunk.

`generate_content_stream` returns an iterator of partial responses. Printing
each chunk as it arrives is what makes chat UIs feel responsive: the first
words show up long before the full answer is finished.
"""

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

prompt = "Write a haiku about Cloud Run cold starts."

for chunk in client.models.generate_content_stream(
    model="gemini-3.5-flash",
    contents=prompt,
):
    # Some chunks carry only metadata and have no text.
    print(chunk.text or "", end="", flush=True)

print()
