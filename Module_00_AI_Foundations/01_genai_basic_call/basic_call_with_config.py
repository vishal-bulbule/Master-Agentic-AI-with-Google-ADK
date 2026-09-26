# Author: Vishal Bulbule
# Date: 2026-09-22

"""GenerateContentConfig, one setting at a time.

Same call as basic_call.py, driven by `types.GenerateContentConfig`. Each
example changes one setting so you can see exactly what it does.

Gemini 3.x models are tuned for the default temperature of 1.0. Google
recommends leaving temperature, top_p and top_k unset for these models; lower
temperatures can cause looping or weaker reasoning. Example 1 still shows the
knob so you know what it does, but prefer system instructions and
`thinking_level` to steer Gemini 3.x.

Run all:         python basic_call_with_config.py
Run one example: python basic_call_with_config.py 3
(numbers match the EXAMPLES list at the bottom)
"""

import json
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

client = genai.Client()

MODEL = "gemini-3.5-flash"


def hr(title: str) -> None:
    print(f"\n{'=' * 64}\n{title}\n{'=' * 64}")


# 1. temperature: sampling randomness. Range 0.0 to 2.0, default 1.0.
def ex_temperature():
    hr("1. TEMPERATURE  (0.0 vs 1.8)")
    prompt = "Give me a one-line tagline for a Cloud Run course."
    for temp in (0.0, 1.8):
        cfg = types.GenerateContentConfig(temperature=temp)
        r = client.models.generate_content(model=MODEL, contents=prompt, config=cfg)
        print(f"temp={temp}: {r.text.strip()}")


# 2. max_output_tokens: hard cap on output length. Thinking tokens count
#    against the cap, so thinking is set to MINIMAL here to leave the budget
#    for visible text. When the cap is hit, finish_reason is MAX_TOKENS.
def ex_max_tokens():
    hr("2. MAX_OUTPUT_TOKENS  (cap causes truncation)")
    cfg = types.GenerateContentConfig(
        max_output_tokens=20,
        thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
    )
    r = client.models.generate_content(
        model=MODEL,
        contents="Explain how Kubernetes scheduling works.",
        config=cfg,
    )
    print("text         :", r.text)
    print("finish_reason:", r.candidates[0].finish_reason, " (MAX_TOKENS means the answer was cut off)")


# 3. system_instruction: the system prompt. Sets persona, rules and voice.
def ex_system_instruction():
    hr("3. SYSTEM_INSTRUCTION  (persona and voice)")
    cfg = types.GenerateContentConfig(
        system_instruction=(
            "You are a terse senior SRE. Answer in at most 2 sentences. "
            "Always mention a production trade-off."
        ),
    )
    r = client.models.generate_content(
        model=MODEL,
        contents="Should I use Cloud Run or GKE?",
        config=cfg,
    )
    print(r.text.strip())


# 4. stop_sequences: generation halts as soon as one of these is produced.
def ex_stop_sequences():
    hr("4. STOP_SEQUENCES  (halt on a marker)")
    cfg = types.GenerateContentConfig(stop_sequences=["3."])
    r = client.models.generate_content(
        model=MODEL,
        contents="List benefits of serverless as a numbered list: 1. 2. 3. 4.",
        config=cfg,
    )
    print(r.text.strip())
    print("\n(output stops right before '3.'; the stop string is not included)")


# 5. candidate_count: several independent answers in one call.
#    response.text only reads candidates[0]; loop to see all of them.
def ex_candidate_count():
    hr("5. CANDIDATE_COUNT  (multiple alternatives)")
    cfg = types.GenerateContentConfig(candidate_count=3)
    r = client.models.generate_content(
        model=MODEL,
        contents="A 4-word slogan for an AI agents course.",
        config=cfg,
    )
    for i, c in enumerate(r.candidates):
        print(f"candidate[{i}]: {c.content.parts[0].text.strip()}")


# 6. JSON mode: response_mime_type forces syntactically valid JSON.
def ex_json_mode():
    hr("6. JSON MODE  (response_mime_type='application/json')")
    cfg = types.GenerateContentConfig(response_mime_type="application/json")
    r = client.models.generate_content(
        model=MODEL,
        contents="Give 3 GCP compute services with a one-line use case each, as JSON.",
        config=cfg,
    )
    data = json.loads(r.text)
    print(json.dumps(data, indent=2))


# 7. response_schema: the output must match a typed shape (a pydantic model).
#    Stronger than JSON mode: you get your schema back, already parsed.
class Service(BaseModel):
    name: str
    category: str
    serverless: bool


def ex_response_schema():
    hr("7. RESPONSE_SCHEMA  (typed structured output)")
    cfg = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=list[Service],
        max_output_tokens=2048,  # backstop against runaway generation
    )
    r = client.models.generate_content(
        model=MODEL,
        contents="List exactly 3 GCP compute services. Return only 3 items.",
        config=cfg,
    )
    for svc in r.parsed:
        print(f"- {svc.name:15} category={svc.category:12} serverless={svc.serverless}")


# 8. thinking_config: how much the model reasons before it answers.
#    Gemini 3.x uses thinking_level (MINIMAL, LOW, MEDIUM, HIGH). The older
#    thinking_budget still works for backward compatibility but is deprecated,
#    and sending both in one request is a 400 error.
def ex_thinking():
    hr("8. THINKING_CONFIG  (MINIMAL vs HIGH)")
    prompt = "If a train leaves at 3pm going 60km/h and another at 4pm going 90km/h, when does the second catch up?"
    for level in ("MINIMAL", "HIGH"):
        cfg = types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_level=level))
        r = client.models.generate_content(model=MODEL, contents=prompt, config=cfg)
        print(f"thinking_level={level:8} -> thoughts_tokens: {r.usage_metadata.thoughts_token_count}")
    print("\n(more thinking tokens means more reasoning, more latency and more cost)")


# 9. safety_settings: per-category blocking thresholds.
#    Thresholds: BLOCK_LOW_AND_ABOVE, BLOCK_MEDIUM_AND_ABOVE, BLOCK_ONLY_HIGH, OFF.
def ex_safety():
    hr("9. SAFETY_SETTINGS  (4 categories, threshold OFF)")
    cfg = types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
    )
    r = client.models.generate_content(
        model=MODEL,
        contents="Explain why input validation matters for security.",
        config=cfg,
    )
    print(r.text.strip()[:300], "[truncated]")
    print("\nsafety_ratings:", r.candidates[0].safety_ratings)


# 10. A production-style config combining the settings above.
def ex_combined():
    hr("10. COMBINED  (a production-style config)")
    cfg = types.GenerateContentConfig(
        system_instruction="You are a concise cloud architecture tutor.",
        max_output_tokens=2048,
        stop_sequences=["END"],
        seed=42,  # best-effort reproducibility, not a guarantee
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
        ],
        thinking_config=types.ThinkingConfig(thinking_level="LOW"),
        # Billing labels are an Agent Platform feature; the Gemini API rejects them.
        labels={"project": "adk-samples", "module": "00"} if client.vertexai else None,
    )
    r = client.models.generate_content(
        model=MODEL,
        contents="In 3 bullets, when should I pick BigQuery over Cloud SQL?",
        config=cfg,
    )
    print(r.text.strip())
    print("\nfinish_reason:", r.candidates[0].finish_reason)
    print("total_tokens :", r.usage_metadata.total_token_count)


EXAMPLES = [
    ex_temperature,         # 1
    ex_max_tokens,          # 2
    ex_system_instruction,  # 3
    ex_stop_sequences,      # 4
    ex_candidate_count,     # 5
    ex_json_mode,           # 6
    ex_response_schema,     # 7
    ex_thinking,            # 8
    ex_safety,              # 9
    ex_combined,            # 10
]


if __name__ == "__main__":
    if len(sys.argv) > 1:
        EXAMPLES[int(sys.argv[1]) - 1]()
    else:
        for fn in EXAMPLES:
            fn()
