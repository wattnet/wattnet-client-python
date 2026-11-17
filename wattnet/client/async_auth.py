"""Async token acquisition and caching for the wattnet async client.

Mirrors `wattnet.client.auth` on top of `aiohttp`:

- `AsyncStaticTokenProvider` wraps a token supplied directly by the caller.
- `AsyncClientCredentialsTokenProvider` exchanges a `client_id` and
  `client_secret` for a bearer token with the OAuth 2.0 `client_credentials`
  grant, caching it until most of its lifetime has passed.
"""

import asyncio
import time
from typing import Any, Dict, Optional, Protocol, Tuple

import aiohttp

from wattnet.client.auth import (
    discovery_url,
    parse_token_response,
    renew_after,
    token_endpoint,
)
from wattnet.client.exceptions import AuthenticationError, WattnetAPIError
from wattnet.client.settings import (
    DEFAULT_RETRY_COUNT,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
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


async def response_error(
    response: aiohttp.ClientResponse,
) -> "tuple[Optional[str], Optional[str]]":
    """Best-effort extraction of the message and the stable code of an error response.

    Reads `detail` (wattnet API) or `error_description` (OAuth 2.0 token endpoint),
    and the `code` that the wattnet API adds to its errors.
    """
    try:
        body = await response.json(content_type=None)
        detail = body.get("detail") or body.get("error_description")
        code = body.get("code")
    except (ValueError, AttributeError, aiohttp.ClientError):
        text = await response.text()
        return text or None, None
    detail = detail if isinstance(detail, str) or detail is None else str(detail)
    return detail, code if isinstance(code, str) else None


async def response_detail(response: aiohttp.ClientResponse) -> Optional[str]:
    """Best-effort extraction of the error message from an error response."""
    return (await response_error(response))[0]


async def _raise_for_status(response: aiohttp.ClientResponse) -> None:
    if response.status in (400, 401, 403):
        raise AuthenticationError(
            await response_detail(response) or "Authentication failed."
        )
    if response.status >= 400:
        detail = await response_detail(response)
        raise WattnetAPIError(
            f"Token request failed ({response.status}): {detail}",
            status_code=response.status,
            detail=detail,
        )


class AsyncClientCredentialsTokenProvider:
    """Exchanges `client_id` and `client_secret` for a bearer token, with caching."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        issuer_url: str,
        token_url: Optional[str],
        session: aiohttp.ClientSession,
        timeout: float = DEFAULT_TIMEOUT,
        retry_count: int = DEFAULT_RETRY_COUNT,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ) -> None:
        """Store credentials; no request is made until `get_token()` is awaited."""
        self._client_id = client_id
        self._client_secret = client_secret
        self._issuer_url = issuer_url
        self._token_url = token_url
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._retry_count = retry_count
        self._retry_delay = retry_delay
        self._lock = asyncio.Lock()
        self._token: Optional[str] = None
        self._renew_at = 0.0  # time.monotonic() value; immune to clock changes

    def set_session(self, session: aiohttp.ClientSession) -> None:
        """Swap the HTTP session (used when the client creates it lazily)."""
        self._session = session

    async def get_token(self) -> str:
        """Return a cached token if still fresh, otherwise fetch a new one."""
        async with self._lock:
            if self._token is None or time.monotonic() >= self._renew_at:
                self._token, self._renew_at = await self._fetch()
            return self._token

    def invalidate(self) -> None:
        """Discard the cached token, forcing the next `get_token()` to refetch."""
        self._token = None

    async def _fetch(self) -> Tuple[str, float]:
        attempts = self._retry_count + 1
        for attempt in range(attempts):
            try:
                return await self._request()
            except TRANSIENT_ERRORS:
                if attempt == attempts - 1:
                    raise
                await asyncio.sleep(self._retry_delay)
        raise AssertionError(
            "unreachable: loop always returns or raises"
        )  # pragma: no cover

    async def _request(self) -> Tuple[str, float]:
        started = time.monotonic()
        endpoint = await self._token_endpoint()
        async with self._session.post(
            endpoint,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            timeout=self._timeout,
        ) as response:
            await _raise_for_status(response)
            payload: Dict[str, Any] = await response.json(content_type=None)
        token, expires_in = parse_token_response(payload)
        return token, started + renew_after(expires_in)

    async def _token_endpoint(self) -> str:
        if self._token_url is None:
            async with self._session.get(
                discovery_url(self._issuer_url), timeout=self._timeout
            ) as response:
                await _raise_for_status(response)
                document = await response.json(content_type=None)
            self._token_url = token_endpoint(document)
        return self._token_url


__all__ = [
    "AsyncTokenProvider",
    "AsyncStaticTokenProvider",
    "AsyncClientCredentialsTokenProvider",
]
