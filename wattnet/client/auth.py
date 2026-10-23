"""Token acquisition and caching for the wattnet client.

Two `TokenProvider` implementations are available:

- `StaticTokenProvider` wraps a token supplied directly by the caller.
- `ClientCredentialsTokenProvider` exchanges a `client_id` and `client_secret`
  for a bearer token with the OAuth 2.0 `client_credentials` grant, caching it
  until most of its lifetime has passed. The token endpoint is read from the
  issuer's OpenID Connect discovery document unless `token_url` is given.
"""

import threading
import time
from typing import Any, Dict, Optional, Protocol, Tuple

import requests

from wattnet.client import decorators
from wattnet.client._util import error_detail
from wattnet.client.exceptions import AuthenticationError, WattnetAPIError, WattnetError
from wattnet.client.settings import (
    DEFAULT_RETRY_COUNT,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    TOKEN_MIN_MARGIN_SECONDS,
    TOKEN_RENEW_FRACTION,
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


def discovery_url(issuer_url: str) -> str:
    """URL of the OpenID Connect discovery document of `issuer_url`."""
    return f"{issuer_url.rstrip('/')}/.well-known/openid-configuration"


def renew_after(expires_in: float) -> float:
    """Seconds after which a token that lives `expires_in` seconds is renewed."""
    return max(
        min(expires_in * TOKEN_RENEW_FRACTION, expires_in - TOKEN_MIN_MARGIN_SECONDS),
        0.0,
    )


def parse_token_response(payload: Dict[str, Any]) -> Tuple[str, float]:
    """Return `(access_token, expires_in)` from a token endpoint response."""
    try:
        return payload["access_token"], float(payload["expires_in"])
    except (KeyError, TypeError, ValueError) as exc:
        raise WattnetError("Unexpected response from the token endpoint.") from exc


def token_endpoint(document: Any) -> str:
    """Return the `token_endpoint` of an OpenID Connect discovery document."""
    try:
        endpoint: str = document["token_endpoint"]
    except (KeyError, TypeError) as exc:
        raise WattnetError(
            "The issuer's discovery document has no `token_endpoint`."
        ) from exc
    return endpoint


class ClientCredentialsTokenProvider:
    """Exchanges `client_id` and `client_secret` for a bearer token, with caching."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        issuer_url: str,
        token_url: Optional[str] = None,
        session: Optional[requests.Session] = None,
        timeout: float = DEFAULT_TIMEOUT,
        retry_count: int = DEFAULT_RETRY_COUNT,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ) -> None:
        """Store credentials; no request is made until `get_token()` is called."""
        self._client_id = client_id
        self._client_secret = client_secret
        self._issuer_url = issuer_url
        self._token_url = token_url
        self._session = session or requests.Session()
        self._timeout = timeout
        self._retry_count = retry_count
        self._retry_delay = retry_delay
        self._lock = threading.Lock()
        self._token: Optional[str] = None
        self._renew_at = 0.0  # time.monotonic() value; immune to clock changes

    def get_token(self) -> str:
        """Return a cached token if still fresh, otherwise fetch a new one."""
        with self._lock:
            if self._token is None or time.monotonic() >= self._renew_at:
                self._token, self._renew_at = self._fetch()
            return self._token

    def invalidate(self) -> None:
        """Discard the cached token, forcing the next `get_token()` to refetch."""
        with self._lock:
            self._token = None

    @decorators.retry()
    def _fetch(self) -> Tuple[str, float]:
        started = time.monotonic()
        response = self._session.post(
            self._token_endpoint(),
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            timeout=self._timeout,
        )
        self._raise_for_status(response)
        token, expires_in = parse_token_response(response.json())
        return token, started + renew_after(expires_in)

    def _token_endpoint(self) -> str:
        if self._token_url is None:
            response = self._session.get(
                discovery_url(self._issuer_url), timeout=self._timeout
            )
            self._raise_for_status(response)
            self._token_url = token_endpoint(response.json())
        return self._token_url

    @staticmethod
    def _raise_for_status(response: requests.Response) -> None:
        if response.status_code in (400, 401, 403):
            raise AuthenticationError(
                error_detail(response) or "Authentication failed."
            )
        if not response.ok:
            detail = error_detail(response)
            raise WattnetAPIError(
                f"Token request failed ({response.status_code}): {detail}",
                status_code=response.status_code,
                detail=detail,
            )
