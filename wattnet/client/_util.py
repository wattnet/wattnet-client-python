"""Small internal helpers shared across the client modules."""

from typing import Any, Optional, cast


def error_detail(response: Any) -> Optional[str]:
    """Best-effort extraction of the error message from an error response.

    Reads `detail` (wattnet API) or `error_description` (OAuth 2.0 token endpoint).
    """
    try:
        body = response.json()
        detail = body.get("detail") or body.get("error_description")
    except (ValueError, AttributeError):
        return cast(Optional[str], response.text) or None
    return cast(Optional[str], detail)


def parse_retry_after(value: Optional[str], default: float) -> float:
    """Seconds to wait before retrying, honoring a numeric `Retry-After`.

    Falls back to `default` if the header is absent or not a plain integer
    (e.g. an HTTP-date value, which we don't bother parsing).
    """
    if value is None:
        return default
    try:
        return max(float(value), 0.0)
    except ValueError:
        return default
