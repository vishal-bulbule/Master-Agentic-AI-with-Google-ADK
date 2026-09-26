# Author: Vishal Bulbule
# Date: 2026-09-22

"""Checklist item 3: input validation helpers for tool arguments.

Tool arguments are written by a model, which may be following instructions
injected by a user or a document. Treat them like form data from a browser:
check type, length, format, and allowlists, and reject bad input with a clear
error instead of truncating or coercing it.

FastMCP validates types from the function signature; Pydantic models or
`Annotated[str, Field(pattern=...)]` parameters give you most of these checks
declaratively. The manual version below shows what is being checked.
"""

import re

SLUG_PATTERN = re.compile(r"^[a-z0-9-]{1,64}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidationError(ValueError):
    """Raised when a tool argument fails validation."""


def validate_slug(slug: str) -> str:
    """Accept 1 to 64 lowercase letters, digits, and hyphens."""
    if not isinstance(slug, str) or not SLUG_PATTERN.match(slug):
        raise ValidationError(f"invalid slug: {slug!r}")
    return slug


def validate_email(email: str) -> str:
    """Accept a plausible email address of at most 254 characters."""
    if not isinstance(email, str) or len(email) > 254 or not EMAIL_PATTERN.match(email):
        raise ValidationError(f"invalid email: {email!r}")
    return email.lower()


def validate_query(query: str, *, max_len: int = 200) -> str:
    """Accept a non-empty search string of at most `max_len` characters."""
    if not isinstance(query, str):
        raise ValidationError("query must be a string")
    query = query.strip()
    if not query or len(query) > max_len:
        raise ValidationError(f"query length must be 1 to {max_len} characters")
    return query
