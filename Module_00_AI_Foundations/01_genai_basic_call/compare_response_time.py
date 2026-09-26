# Author: Vishal Bulbule
# Date: 2026-09-22

"""Time the same call on two models.

Flash is built for low latency. Pro spends more time reasoning. The gap you see
here is the latency cost of the bigger model, before you look at price.

If a model is not enabled for your project (an organization policy can block
Pro models), that model prints the API error and the script moves on.
"""

import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

client = genai.Client()

prompt = "Summarize in one sentence: An AI agent is an LLM with autonomy, tools, memory, and a loop."

models = ["gemini-3.5-flash", "gemini-2.5-pro"]

for model in models:
    start = time.perf_counter()
    try:
        response = client.models.generate_content(model=model, contents=prompt)
    except errors.APIError as e:
        print(f"\n{model}: skipped ({e.code} {e.status})")
        continue
    elapsed = time.perf_counter() - start

    print(f"\n{'=' * 60}\n{model}  {elapsed:.2f}s\n{'=' * 60}")
    print(response.text)
