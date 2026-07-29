"""
Short code generation utilities.

Strategy: random Base62 (a-z, A-Z, 0-9).
On collision the caller generates a new code and retries — enforced by
the DB unique constraint on `short_code`.
"""

from __future__ import annotations

import secrets
import string

BASE62 = string.ascii_letters + string.digits  # 62 characters


def generate_short_code(length: int = 7) -> str:
    """
    Generate a cryptographically random Base62 short code.

    With length=7 the keyspace is 62^7 ≈ 3.5 trillion codes, which
    gives negligible collision probability at the target scale of 1B URLs.
    """
    return "".join(secrets.choice(BASE62) for _ in range(length))


def is_valid_short_code(value: str) -> bool:
    """Return True if the string contains only Base62 characters."""
    return bool(value) and all(c in BASE62 for c in value)
