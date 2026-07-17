"""Small internal helpers shared across the client modules."""

from typing import Optional, cast

import requests


def error_detail(response: requests.Response) -> Optional[str]:
    """Best-effort extraction of the `detail` field from an error response."""
    try:
        detail = response.json().get("detail")
    except (ValueError, AttributeError):
        return response.text or None
    return cast(Optional[str], detail)
