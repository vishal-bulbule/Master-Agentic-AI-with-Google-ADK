# Author: Vishal Bulbule
# Date: 2026-09-22

"""A single Gemini call with the google-genai SDK, then every field of the response.

This is the primitive that ADK builds on. `genai.Client()` reads its settings
from the environment: GOOGLE_API_KEY for the Gemini API, or
GOOGLE_GENAI_USE_ENTERPRISE=TRUE plus GOOGLE_CLOUD_PROJECT and
GOOGLE_CLOUD_LOCATION for Agent Platform (formerly Vertex AI).

After the answer, the script prints the response object section by section.
Look at `usage_metadata`: `thoughts_token_count` is the reasoning the model did
before answering, and it is billed as output.
"""

import json

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Summarize in one sentence: An AI agent is an LLM with autonomy, tools, memory, and a loop.",
)

print(response.text)


def hr(title: str) -> None:
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


hr("TOP-LEVEL FIELDS")
print("response_id      :", response.response_id)
print("model_version    :", response.model_version)
print("create_time      :", response.create_time)
print("prompt_feedback  :", response.prompt_feedback)
print("parsed           :", response.parsed)
print("automatic_function_calling_history:", response.automatic_function_calling_history)

hr("CANDIDATES")
for i, candidate in enumerate(response.candidates):
    print(f"\n--- Candidate[{i}] ---")
    print("finish_reason :", candidate.finish_reason)
    print("avg_logprobs  :", candidate.avg_logprobs)
    print("safety_ratings:", candidate.safety_ratings)

    content = candidate.content
    print("content.role  :", content.role)
    for j, part in enumerate(content.parts):
        print(f"\n  part[{j}].text:")
        print(part.text)

hr("USAGE METADATA")
usage = response.usage_metadata
print("prompt_token_count    :", usage.prompt_token_count)
print("candidates_token_count:", usage.candidates_token_count)
print("thoughts_token_count  :", usage.thoughts_token_count)
print("total_token_count     :", usage.total_token_count)
print("traffic_type          :", usage.traffic_type)

print("\nprompt_tokens_details:")
for d in usage.prompt_tokens_details or []:
    print(f"  modality={d.modality}  token_count={d.token_count}")

print("candidates_tokens_details:")
for d in usage.candidates_tokens_details or []:
    print(f"  modality={d.modality}  token_count={d.token_count}")

hr("FULL RESPONSE AS DICT")
print(json.dumps(response.model_dump(exclude_none=True), indent=2, default=str))
