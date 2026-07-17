"""Token acquisition and caching for the wattnet client.

Two `TokenProvider` implementations are available:

- `StaticTokenProvider` wraps a token supplied directly by the caller.
- `CredentialsTokenProvider` exchanges an email/password pair for a bearer
  token against the wattnet token-request service, caching it until the
  server-reported `expires_at` (minus a small safety margin) is reached.

`register()` is a standalone helper for the token-request service's
`/register` endpoint — call it once per email before a
`CredentialsTokenProvider` (or `WattnetClient(email=..., password=...)`) can
fetch tokens for it.
"""

import threading
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Protocol, Tuple

import requests

from wattnet.client import decorators
from wattnet.client._util import error_detail
from wattnet.client.exceptions import AuthenticationError, WattnetAPIError
from wattnet.client.settings import (
    DEFAULT_RETRY_COUNT,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    DEFAULT_TOKEN_URL,
    TOKEN_EXPIRY_SAFETY_MARGIN_SECONDS,
)


class TokenProvider(Protocol):
    """Something that can hand out a bearer token, and be told to refresh it."""

    def get_token(self) -> str:
        """Return a valid bearer token, fetching or refreshing it if needed."""

    def invalidate(self) -> None:
        """Discard any cached token, forcing the next `get_token()` to refetch."""


class StaticTokenProvider:
    """Hands out a fixed, user-supplied token. Nothing to cache or refresh."""

    def __init__(self, token: str) -> None:
        """Wrap the given fixed token."""
        self._token = token

    def get_token(self) -> str:
        """Return the fixed token."""
        return self._token

    def invalidate(self) -> None:
        """No-op: a static token cannot be refreshed by this client."""


def _parse_expires_at(expires_at: str) -> datetime:
    # The token-issuer returns e.g. "2026-07-16T14:23:45.123456Z"; `fromisoformat`
    # only accepts the "Z" suffix from Python 3.11 onwards, so normalize it here.
    return datetime.fromisoformat(expires_at.replace("Z", "+00:00"))


def _post_token_service(
    token_url: str,
    path: str,
    payload: Dict[str, str],
    session: requests.Session,
    timeout: float,
) -> Dict[str, Any]:
    response = session.post(
        f"{token_url.rstrip('/')}/{path}", json=payload, timeout=timeout
    )
    if response.status_code in (401, 403):
        raise AuthenticationError(error_detail(response) or "Authentication failed.")
    if not response.ok:
        detail = error_detail(response)
        raise WattnetAPIError(
            f"Token service request to /{path} failed ({response.status_code}): "
            f"{detail}",
            status_code=response.status_code,
            detail=detail,
        )
    result: Dict[str, Any] = response.json()
    return result


class CredentialsTokenProvider:
    """Exchanges email/password for a bearer token, caching it until it expires."""

    def __init__(
        self,
        email: str,
        password: str,
        token_url: str,
        session: Optional[requests.Session] = None,
        timeout: float = DEFAULT_TIMEOUT,
        retry_count: int = DEFAULT_RETRY_COUNT,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ) -> None:
        """Store credentials; no request is made until `get_token()` is called."""
        self._email = email
        self._password = password
        self._token_url = token_url.rstrip("/")
        self._session = session or requests.Session()
        self._timeout = timeout
        self._retry_count = retry_count
        self._retry_delay = retry_delay
        self._lock = threading.Lock()
        self._token: Optional[str] = None
        self._expires_at: Optional[datetime] = None

    def get_token(self) -> str:
        """Return a cached token if still fresh, otherwise fetch a new one."""
        with self._lock:
            if self._token is None or self._is_stale():
                self._token, self._expires_at = self._fetch()
            return self._token

    def invalidate(self) -> None:
        """Discard the cached token, forcing the next `get_token()` to refetch."""
        with self._lock:
            self._token = None
            self._expires_at = None

    def _is_stale(self) -> bool:
        if self._expires_at is None:
            return True
        now = datetime.now(timezone.utc)
        safe_expiry = self._expires_at.timestamp() - TOKEN_EXPIRY_SAFETY_MARGIN_SECONDS
        return now.timestamp() >= safe_expiry

    @decorators.retry()
    def _fetch(self) -> Tuple[str, datetime]:
        payload = _post_token_service(
            self._token_url,
            "get_token",
            {"email": self._email, "password": self._password},
            self._session,
            self._timeout,
        )
        return payload["access_token"], _parse_expires_at(payload["expires_at"])


@decorators.retry(count=DEFAULT_RETRY_COUNT, delay=DEFAULT_RETRY_DELAY)
def register(
    email: str,
    password: str,
    token_url: str = DEFAULT_TOKEN_URL,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    """Register an email/password pair with the wattnet token-request service.

    Must be called once per email before it can be used with
    `CredentialsTokenProvider` or `WattnetClient(email=..., password=...)` —
    `email` must already be pre-authorized server-side by the wattnet team.
    Calling it again for an already-registered email is a harmless no-op.

    :return: the server's confirmation message, e.g. "User registered
        successfully." or "User already registered."
    :raises AuthenticationError: if `email` is not pre-authorized (403).
    :raises WattnetAPIError: on any other non-2xx response.
    """
    payload = _post_token_service(
        token_url,
        "register",
        {"email": email, "password": password},
        session or requests.Session(),
        timeout,
    )
    message: str = payload["message"]
    return message
