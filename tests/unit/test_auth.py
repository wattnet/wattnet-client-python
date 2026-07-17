"""Tests for wattnet.client.auth token providers."""

from datetime import datetime, timedelta, timezone

import pytest
import requests
import responses

from wattnet.client.auth import CredentialsTokenProvider, StaticTokenProvider, register
from wattnet.client.exceptions import AuthenticationError, WattnetAPIError

TOKEN_URL = "https://wattnet-api.test/token-request"


def test_static_token_provider_returns_fixed_token():
    provider = StaticTokenProvider("fixed-token")

    assert provider.get_token() == "fixed-token"
    provider.invalidate()  # no-op, must not raise
    assert provider.get_token() == "fixed-token"


def _expires_at(delta: timedelta) -> str:
    return (datetime.now(timezone.utc) + delta).isoformat().replace("+00:00", "Z")


@responses.activate
def test_credentials_token_provider_fetches_and_caches():
    responses.add(
        responses.POST,
        f"{TOKEN_URL}/get_token",
        json={"access_token": "abc123", "expires_at": _expires_at(timedelta(hours=24))},
        status=200,
    )
    provider = CredentialsTokenProvider("user@example.com", "secret", TOKEN_URL)

    assert provider.get_token() == "abc123"
    assert provider.get_token() == "abc123"
    assert len(responses.calls) == 1  # second call served from cache


@responses.activate
def test_credentials_token_provider_refetches_after_expiry():
    responses.add(
        responses.POST,
        f"{TOKEN_URL}/get_token",
        json={
            "access_token": "first",
            "expires_at": _expires_at(-timedelta(seconds=1)),
        },
        status=200,
    )
    responses.add(
        responses.POST,
        f"{TOKEN_URL}/get_token",
        json={"access_token": "second", "expires_at": _expires_at(timedelta(hours=24))},
        status=200,
    )
    provider = CredentialsTokenProvider("user@example.com", "secret", TOKEN_URL)

    assert provider.get_token() == "first"
    assert provider.get_token() == "second"
    assert len(responses.calls) == 2


@responses.activate
def test_credentials_token_provider_invalidate_forces_refetch():
    responses.add(
        responses.POST,
        f"{TOKEN_URL}/get_token",
        json={"access_token": "first", "expires_at": _expires_at(timedelta(hours=24))},
        status=200,
    )
    responses.add(
        responses.POST,
        f"{TOKEN_URL}/get_token",
        json={"access_token": "second", "expires_at": _expires_at(timedelta(hours=24))},
        status=200,
    )
    provider = CredentialsTokenProvider("user@example.com", "secret", TOKEN_URL)

    assert provider.get_token() == "first"
    provider.invalidate()
    assert provider.get_token() == "second"


@responses.activate
def test_credentials_token_provider_invalid_credentials():
    responses.add(
        responses.POST,
        f"{TOKEN_URL}/get_token",
        json={"detail": "Invalid credentials."},
        status=401,
    )
    provider = CredentialsTokenProvider("user@example.com", "wrong", TOKEN_URL)

    with pytest.raises(AuthenticationError):
        provider.get_token()


@responses.activate
def test_credentials_token_provider_upstream_failure():
    responses.add(
        responses.POST,
        f"{TOKEN_URL}/get_token",
        json={"detail": "Failed to obtain token from Keycloak"},
        status=500,
    )
    provider = CredentialsTokenProvider("user@example.com", "secret", TOKEN_URL)

    with pytest.raises(WattnetAPIError) as exc_info:
        provider.get_token()
    assert exc_info.value.status_code == 500


def test_credentials_token_provider_is_stale_before_any_fetch():
    # _is_stale() is only reachable via get_token() once a token was already
    # fetched (its `self._token is None` short-circuit skips it on the very
    # first call), so exercise the "never fetched yet" branch directly.
    provider = CredentialsTokenProvider("user@example.com", "secret", TOKEN_URL)

    assert provider._is_stale() is True


@responses.activate
def test_credentials_token_provider_retries_transient_network_errors():
    provider = CredentialsTokenProvider(
        "user@example.com", "secret", TOKEN_URL, retry_count=2, retry_delay=0
    )
    responses.add(
        responses.POST,
        f"{TOKEN_URL}/get_token",
        body=requests.exceptions.ConnectionError("boom"),
    )
    responses.add(
        responses.POST,
        f"{TOKEN_URL}/get_token",
        json={"access_token": "abc123", "expires_at": _expires_at(timedelta(hours=24))},
        status=200,
    )

    assert provider.get_token() == "abc123"
    assert len(responses.calls) == 2


@responses.activate
def test_register_returns_confirmation_message():
    responses.add(
        responses.POST,
        f"{TOKEN_URL}/register",
        json={"message": "User registered successfully."},
        status=200,
    )

    assert register("user@example.com", "secret", TOKEN_URL) == (
        "User registered successfully."
    )


@responses.activate
def test_register_rejects_unauthorized_email():
    responses.add(
        responses.POST,
        f"{TOKEN_URL}/register",
        json={"detail": "Not authorized access."},
        status=403,
    )

    with pytest.raises(AuthenticationError):
        register("nobody@example.com", "secret", TOKEN_URL)


@responses.activate
def test_register_raises_wattnet_api_error_on_upstream_failure():
    responses.add(
        responses.POST,
        f"{TOKEN_URL}/register",
        json={"detail": "Internal error"},
        status=500,
    )

    with pytest.raises(WattnetAPIError) as exc_info:
        register("user@example.com", "secret", TOKEN_URL)
    assert exc_info.value.status_code == 500
