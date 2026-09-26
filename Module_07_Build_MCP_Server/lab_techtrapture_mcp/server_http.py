# Author: Vishal Bulbule
# Date: 2026-09-22

"""techtrapture-mcp over Streamable HTTP, for Cloud Run.

Imports the server defined in server_stdio.py and serves it with FastMCP's
ASGI app at /mcp. `stateless_http=True` builds a fresh transport per request,
so any Cloud Run instance can answer any request and the service scales out
without sticky sessions.

`mcp.http_app()` returns a Starlette app with the session manager's lifespan
already wired in. To add auth or rate limiting, pass
`middleware=[Middleware(...)]` (see ../06_security_checklist/).

Run:
    python server_http.py      # http://0.0.0.0:8080/mcp (PORT overrides)
"""

import os

import uvicorn

from server_stdio import mcp

app = mcp.http_app(path="/mcp", stateless_http=True)

if __name__ == "__main__":
    # Cloud Run sets PORT. 0.0.0.0 is required inside a container.
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
