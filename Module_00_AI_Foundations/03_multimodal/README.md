<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# Multimodal input

## What this shows

One `generate_content` call that carries an image and a text prompt together.
The `contents` list can mix strings and PIL images; the SDK turns each image
into an inline image part.

## Prerequisites

- [ ] Repository setup done ([SETUP.md](../../SETUP.md)): virtual environment
      and `pip install -r requirements.txt`.
- [ ] Credentials in a `.env` at the repository root or in this folder, with
      the variables from [`.env.example`](.env.example): `GOOGLE_API_KEY`, or
      Agent Platform (formerly Vertex AI) with `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`,
      `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION=global`
      (`gemini-3.5-flash` is served from `global`).
- [ ] Optional: a PNG or JPG of your own (a chart, dashboard or diagram).
      Without one, the script draws a sample bar chart with Pillow.

## Run it

1. `cd Module_00_AI_Foundations/03_multimodal`
2. `python multimodal_call.py` (uses the generated sample chart)
3. `python multimodal_call.py path/to/image.png` (uses your own image)

## What to look for

With the built-in chart, the model should read the month labels and values and
describe an upward trend. Try a screenshot of a dashboard or an architecture
diagram and compare how much detail it extracts.
