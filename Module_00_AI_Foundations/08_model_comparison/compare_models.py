# Author: Vishal Bulbule
# Date: 2026-09-22

"""Run one reasoning prompt on Flash and Pro and compare latency and tokens.

Pick the smallest model that answers correctly. The printout shows the
trade-off directly: wall-clock latency, input tokens, output tokens and
thinking tokens (billed as output) for each model.

If a model is not enabled for your project (an organization policy can block
Pro models), that model prints the API error and the script moves on.
"""

import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

client = genai.Client()

PROMPT = (
    "A train leaves A at 60 km/h and another leaves B at 90 km/h toward each other. "
    "Distance A to B is 300 km. When do they meet?"
)

MODELS = ["gemini-3.5-flash", "gemini-2.5-pro"]

for model in MODELS:
    start = time.perf_counter()
    try:
        resp = client.models.generate_content(model=model, contents=PROMPT)
    except errors.APIError as e:
        print(f"\n=== {model}: skipped ({e.code} {e.status}) ===")
        continue
    elapsed = time.perf_counter() - start
    m = resp.usage_metadata
    print(f"\n=== {model} ({elapsed:.2f}s) ===")
    print(f"input={m.prompt_token_count}  output={m.candidates_token_count}  thinking={m.thoughts_token_count}")
    print(resp.text)
