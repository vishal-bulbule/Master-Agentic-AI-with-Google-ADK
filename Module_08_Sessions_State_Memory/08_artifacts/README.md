<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 08 Artifacts

## What this shows

State is for small JSON values. Files (PDFs, images, audio) belong in
artifacts: state values must be JSON-serializable and raw bytes are not,
every save of the same filename creates a new version, and artifacts are
stored outside the conversation, so they do not fill the model's context.
`save_pdf_report` builds a one-page PDF in code (standard library only) and
saves it; `load_pdf_artifact` loads it and reports size and MIME type.

```python
part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
version = await tool_context.save_artifact("report.pdf", part)   # 0, 1, 2, ...

loaded = await tool_context.load_artifact("report.pdf")          # latest version
pdf_bytes = loaded.inline_data.data
```

The artifact store is chosen with `--artifact_service_uri`: `memory://`
(in process), `file:///absolute/dir` (`FileArtifactService`), or
`gs://<bucket>` (`GcsArtifactService`). With no URI, `adk web` uses
`<agent>/.adk/artifacts`. The tools do not change. Prefix a filename with
`user:` (for example `user:report.pdf`) to share it across the user's
sessions.

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)) and a `.env` with your Gemini
  settings (see `artifact_agent/.env.example`; on Agent Platform use
  `GOOGLE_CLOUD_LOCATION=global`).
- Only for `gs://`: an existing Cloud Storage bucket and Application Default
  Credentials with write access to it. This sample is tested with `memory://`.

## Run it

1. `cd Module_08_Sessions_State_Memory/08_artifacts`
2. `adk web --session_service_uri=memory:// --artifact_service_uri=memory:// --memory_service_uri=memory://`
3. Open http://localhost:8000 and select `artifact_agent` in the agent dropdown.
4. Send: "Create a PDF called report.pdf titled Quarterly summary saying revenue grew 12 percent."

## Try it

1. The prompt above.
2. "Save it again as report.pdf with the title Quarterly summary v2."
3. "Load report.pdf back and tell me its size and type."

List the versions over REST (replace `<session-id>`; the dev UI user is
`user`):

```bash
curl http://127.0.0.1:8000/apps/artifact_agent/users/user/sessions/<session-id>/artifacts/report.pdf/versions
```

## What to look for

- The first save returns `version: 0`, the second `version: 1`.
- The load reports `application/pdf` and the size of version 1.
- The Artifacts tab lists `report.pdf`; open it to view the PDF. The versions
  endpoint returns `[0, 1]`.
