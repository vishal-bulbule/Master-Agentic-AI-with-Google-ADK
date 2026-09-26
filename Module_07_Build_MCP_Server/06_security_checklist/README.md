<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 06: Security Checklist

## What this shows

MCP does not secure a server for you. The protocol defines messages, not
policy, so a deployed server needs the controls below. Four have code in this
folder; three are design rules explained here.

| # | Item | Code |
|---|---|---|
| 1 | Authentication | `auth.py`: `BearerAuthMiddleware` |
| 2 | Expose only the tools callers need | Design rule |
| 3 | Input validation | `validate.py` |
| 4 | Path restrictions | Design rule |
| 5 | Rate limiting | `rate_limit.py`: `RateLimitMiddleware` |
| 6 | Audit logging | `audit.py`: `@audit_tool` |
| 7 | Read-only by default | Design rule |

## Prerequisites

- Repository setup ([SETUP.md](../../SETUP.md)), virtual environment active.
- Node.js with `npx`, for the MCP Inspector CLI check.
- No API keys. The bearer tokens are any strings you choose, passed in
  `MCP_BEARER_TOKENS`.

## Run it

`auth.py`, `rate_limit.py`, `validate.py`, and `audit.py` are modules to
import into your server, not servers themselves. To see them work together:

1. `cd Module_07_Build_MCP_Server/06_security_checklist`
2. Save this as `secured_server.py` in this folder (so the imports resolve):

   ```python
   import logging

   import uvicorn
   from fastmcp import FastMCP
   from starlette.middleware import Middleware

   from audit import audit_tool
   from auth import BearerAuthMiddleware
   from rate_limit import RateLimitMiddleware
   from validate import validate_email, validate_slug

   logging.basicConfig(level=logging.INFO)  # shows the audit lines

   mcp = FastMCP("secured-server")


   @mcp.tool()
   @audit_tool("enroll_student", log_values_for=("course_slug",))
   def enroll_student(course_slug: str, email: str) -> dict:
       course_slug = validate_slug(course_slug)
       email = validate_email(email)
       return {"status": "success", "course_slug": course_slug}


   # Starlette runs the first middleware in the list outermost.
   app = mcp.http_app(
       stateless_http=True,
       middleware=[
           Middleware(BearerAuthMiddleware),
           Middleware(RateLimitMiddleware, capacity=30, refill_per_second=0.5),
       ],
   )

   if __name__ == "__main__":
       uvicorn.run(app, host="127.0.0.1", port=8080)
   ```

3. `MCP_BEARER_TOKENS=token-a,token-b python secured_server.py`
4. In another terminal:

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8080/mcp   # 401
   npx @modelcontextprotocol/inspector --cli http://127.0.0.1:8080/mcp \
     --header "Authorization: Bearer token-a" \
     --method tools/call --tool-name enroll_student \
     --tool-arg course_slug=adk-bootcamp --tool-arg email=a@example.com
   npx @modelcontextprotocol/inspector --cli http://127.0.0.1:8080/mcp \
     --header "Authorization: Bearer token-a" \
     --method tools/call --tool-name enroll_student \
     --tool-arg "course_slug=BAD SLUG" --tool-arg email=a@example.com
   ```

Expected: 401 without a token (403 with a wrong one), a success result for
the valid call, `"isError": true` with `invalid slug: 'BAD SLUG'` for the
second, and one `mcp_tool_call` JSON line per call in the server log.

## What to look for

### 1. Authentication

Every request needs `Authorization: Bearer <token>`: 401 without one, 403
with a wrong one. The check runs on every request, not once per session.
On Cloud Run, IAM is usually better: `--no-allow-unauthenticated` plus
`roles/run.invoker` for the calling service account makes Google verify an
identity token before your code runs.

### 2. Expose only the tools callers need

If `lookup_customer` can return personal data, split it: a public
`lookup_customer_summary` (name and tier) on this server, and
`lookup_customer_full` on a separate server with stricter IAM. Do not import
internal tools into a public server at all; a client-side `tool_filter` is
the caller's choice, not your control.

### 3. Input validation

The model writes the arguments, possibly following text injected by a user
or a document. Validate type, length, format, and allowlists; raise a clear
error instead of truncating. Raising inside a FastMCP tool returns an MCP
error result (`isError: true`) to the caller.

### 4. Path restrictions

For file-backed servers, resolve every path and reject anything outside an
allowed root before opening it:

```python
from pathlib import Path

ALLOWED_ROOT = Path("/srv/data").resolve()


def safe_open(rel_path: str):
    full = (ALLOWED_ROOT / rel_path).resolve()
    if not full.is_relative_to(ALLOWED_ROOT):
        raise PermissionError("path escapes the allowed root")
    return full.open()
```

`resolve()` follows `..` and symlinks, so `../../etc/passwd` and a symlink
out of the root are both rejected.

### 5. Rate limiting

`RateLimitMiddleware` keeps a token bucket per caller and returns 429 when it
is empty. The buckets are per instance; for a global limit use Redis
(Memorystore) or rate-limit in front of the service (Cloud Armor, API
Gateway).

### 6. Audit logging

`@audit_tool` writes one JSON line per call: tool, argument names, outcome,
duration. Values are logged only for arguments you list in `log_values_for`,
so emails and other personal data stay out of the logs. Cloud Logging parses
the JSON lines from stdout into structured entries.

### 7. Read-only by default

Make write tools opt-in at deploy time:

```python
import os

WRITES_ENABLED = os.environ.get("MCP_WRITES", "false").lower() == "true"


@mcp.tool()
def enroll_student(course_slug: str, email: str) -> dict:
    if not WRITES_ENABLED:
        raise PermissionError("server is read-only; set MCP_WRITES=true")
    ...
```

Or deploy two services from the same code: a read-only one for broad use and
a read-write one restricted by IAM.

### Middleware order

Outermost first:

1. Authentication: reject unauthenticated requests before doing any work.
2. Rate limiting: after auth, so buckets are per caller, not per IP.
3. The MCP endpoint, with audit logging inside each tool.

## Clean up

`rm secured_server.py` if you created it.
