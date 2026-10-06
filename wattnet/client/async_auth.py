"""Async token acquisition and caching for the wattnet async client.

Mirrors `wattnet.client.auth` on top of `aiohttp`:

- `AsyncStaticTokenProvider` wraps a token supplied directly by the caller.
- `AsyncCredentialsTokenProvider` exchanges an email/password pair for a
  bearer token against the wattnet token-request service, caching it until
  the server-reported `expires_at` (minus a small safety margin) is reached.

`async_register()` is the async counterpart of `wattnet.client.register`.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Protocol, Tuple

import aiohttp

from wattnet.client.auth import _parse_expires_at
from wattnet.client.exceptions import AuthenticationError, WattnetAPIError
from wattnet.client.settings import (
    DEFAULT_RETRY_COUNT,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    DEFAULT_TOKEN_URL,
    TOKEN_EXPIRY_SAFETY_MARGIN_SECONDS,
)

TRANSIENT_ERRORS = (aiohttp.ClientConnectionError, asyncio.TimeoutError)


class AsyncTokenProvider(Protocol):
    """Something that can hand out a bearer token, and be told to refresh it."""

    async def get_token(self) -> str:
        """Return a valid bearer token, fetching or refreshing it if needed."""

    def invalidate(self) -> None:
        """Discard any cached token, forcing the next `get_token()` to refetch."""


class AsyncStaticTokenProvider:
    """Hands out a fixed, user-supplied token. Nothing to cache or refresh."""

    def __init__(self, token: str) -> None:
        """Wrap the given fixed token."""
        self._token = token

    async def get_token(self) -> str:
        """Return the fixed token."""
        return self._token

    def invalidate(self) -> None:
        """No-op: a static token cannot be refreshed by this client."""


async def response_detail(response: aiohttp.ClientResponse) -> Optional[str]:
    """Best-effort extraction of the `detail` field from an error response."""
    try:
        body = await response.json(content_type=None)
        detail = body.get("detail")
    except (ValueError, AttributeError, aiohttp.ClientError):
        text = await response.text()
        return text or None
    return detail if isinstance(detail, str) or detail is None else str(detail)


async def _post_token_service(
    session: aiohttp.ClientSession,
    token_url: str,
    path: str,
    payload: Dict[str, str],
    timeout: float,
) -> Dict[str, Any]:
    async with session.post(
        f"{token_url.rstrip('/')}/{path}",
        json=payload,
        timeout=aiohttp.ClientTimeout(total=timeout),
    ) as response:
        if response.status in (401, 403):
            raise AuthenticationError(
                await response_detail(response) or "Authentication failed."
            )
        if response.status >= 400:
            detail = await response_detail(response)
            raise WattnetAPIError(
                f"Token service request to /{path} failed ({response.status}): "
                f"{detail}",
                status_code=response.status,
                detail=detail,
            )
        result: Dict[str, Any] = await response.json(content_type=None)
        return result


async def _post_with_retry(
    session: aiohttp.ClientSession,
    token_url: str,
    path: str,
    payload: Dict[str, str],
    timeout: float,
    retry_count: int,
    retry_delay: float,
) -> Dict[str, Any]:
    """POST to the token service, retrying transient network errors."""
    attempts = retry_count + 1
    for attempt in range(attempts):
        is_last_attempt = attempt == attempts - 1
        try:
            return await _post_token_service(session, token_url, path, payload, timeout)
        except TRANSIENT_ERRORS:
            if is_last_attempt:
                raise
            await asyncio.sleep(retry_delay)
    raise AssertionError(
        "unreachable: loop always returns or raises"
    )  # pragma: no cover


class AsyncCredentialsTokenProvider:
    """Exchanges email/password for a bearer token, caching it until it expires."""

    def __init__(
        self,
        email: str,
        password: str,
        token_url: str,
        session: aiohttp.ClientSession,
        timeout: float = DEFAULT_TIMEOUT,
        retry_count: int = DEFAULT_RETRY_COUNT,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ) -> None:
        """Store credentials; no request is made until `get_token()` is awaited."""
        self._email = email
        self._password = password
        self._token_url = token_url.rstrip("/")
        self._session = session
        self._timeout = timeout
        self._retry_count = retry_count
        self._retry_delay = retry_delay
        self._lock = asyncio.Lock()
        self._token: Optional[str] = None
        self._expires_at: Optional[datetime] = None

    def set_session(self, session: aiohttp.ClientSession) -> None:
        """Swap the HTTP session (used when the client creates it lazily)."""
        self._session = session

    async def get_token(self) -> str:
        """Return a cached token if still fresh, otherwise fetch a new one."""
        async with self._lock:
            if self._token is None or self._is_stale():
                self._token, self._expires_at = await self._fetch()
            return self._token

    def invalidate(self) -> None:
        """Discard the cached token, forcing the next `get_token()` to refetch."""
        self._token = None
        self._expires_at = None

    def _is_stale(self) -> bool:
        if self._expires_at is None:
            return True
        now = datetime.now(timezone.utc)
        safe_expiry = self._expires_at.timestamp() - TOKEN_EXPIRY_SAFETY_MARGIN_SECONDS
        return now.timestamp() >= safe_expiry

    async def _fetch(self) -> Tuple[str, datetime]:
        payload = await _post_with_retry(
            self._session,
            self._token_url,
            "get_token",
            {"email": self._email, "password": self._password},
            self._timeout,
            self._retry_count,
            self._retry_delay,
        )
        return payload["access_token"], _parse_expires_at(payload["expires_at"])


async def async_register(
    email: str,
    password: str,
    token_url: str = DEFAULT_TOKEN_URL,
    session: Optional[aiohttp.ClientSession] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    """Register an email/password pair with the wattnet token-request service.

    Async counterpart of `wattnet.client.register`: `email` must already be
    pre-authorized server-side by the wattnet team, and calling it again for an
    already-registered email is a harmless no-op.

    :return: the server's confirmation message, e.g. "User registered
        successfully." or "User already registered."
    :raises AuthenticationError: if `email` is not pre-authorized (403).
    :raises WattnetAPIError: on any other non-2xx response.
    """
    owns_session = session is None
    http = session or aiohttp.ClientSession()
    try:
        payload = await _post_with_retry(
            http,
            token_url,
            "register",
            {"email": email, "password": password},
            timeout,
            DEFAULT_RETRY_COUNT,
            DEFAULT_RETRY_DELAY,
        )
    finally:
        if owns_session:
            await http.close()
    message: str = payload["message"]
    return message


__all__ = [
    "AsyncTokenProvider",
    "AsyncStaticTokenProvider",
    "AsyncCredentialsTokenProvider",
    "async_register",
]
