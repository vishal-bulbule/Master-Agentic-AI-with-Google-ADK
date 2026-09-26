# Author: Vishal Bulbule
# Date: 2026-09-22

"""Ground a Gemini answer in Google Search results.

Adding `types.Tool(google_search=types.GoogleSearch())` lets the model run
searches on the server side and answer from current web results instead of
its training data. No tool function runs on your machine.

The answer is followed by the search queries the model issued and the sources
it cited, taken from `candidate.grounding_metadata`. Run it once with the
`tools` line removed from the config to compare against an ungrounded answer.
"""

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

config = types.GenerateContentConfig(
    tools=[types.Tool(google_search=types.GoogleSearch())],
)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="What is the latest released version of the google-adk Python package?",
    config=config,
)

print(response.text)

metadata = response.candidates[0].grounding_metadata
if metadata:
    print("\nSearch queries:", metadata.web_search_queries)
    print("Sources:")
    for chunk in metadata.grounding_chunks or []:
        if chunk.web:
            print(f"  - {chunk.web.title}: {chunk.web.uri}")
else:
    print("\n(no grounding metadata: the model answered without searching)")
