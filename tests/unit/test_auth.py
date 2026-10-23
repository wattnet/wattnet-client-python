"""Tests for wattnet.client.auth token providers."""

from urllib.parse import parse_qs

import pytest
import requests
import responses

from wattnet.client.auth import (
    ClientCredentialsTokenProvider,
    StaticTokenProvider,
    renew_after,
)
from wattnet.client.exceptions import (
    AuthenticationError,
    WattnetAPIError,
    WattnetError,
)

ISSUER_URL = "https://auth.wattnet.test/realms/wattnet"
DISCOVERY_URL = f"{ISSUER_URL}/.well-known/openid-configuration"
TOKEN_URL = f"{ISSUER_URL}/protocol/openid-connect/token"


def _token(name: str, expires_in: int = 3600):
    return {"access_token": name, "expires_in": expires_in, "token_type": "Bearer"}


def _provider(**kwargs) -> ClientCredentialsTokenProvider:
    kwargs.setdefault("retry_delay", 0)
    return ClientCredentialsTokenProvider("cred-id", "s3cret", ISSUER_URL, **kwargs)


def test_static_token_provider_returns_fixed_token():
    provider = StaticTokenProvider("fixed-token")

    assert provider.get_token() == "fixed-token"
    provider.invalidate()  # no-op, must not raise
    assert provider.get_token() == "fixed-token"


@pytest.mark.parametrize(
    "expires_in, expected",
    [(3600, 2880), (300, 240), (100, 40), (60, 0), (30, 0)],
)
def test_renew_after(expires_in, expected):
    assert renew_after(expires_in) == expected


@responses.activate
def test_provider_discovers_token_endpoint_and_sends_the_grant():
    responses.add(
        responses.GET, DISCOVERY_URL, json={"token_endpoint": TOKEN_URL}, status=200
    )
    responses.add(responses.POST, TOKEN_URL, json=_token("abc123"), status=200)

    assert _provider().get_token() == "abc123"

    form = parse_qs(responses.calls[1].request.body)
    assert form == {
        "grant_type": ["client_credentials"],
        "client_id": ["cred-id"],
        "client_secret": ["s3cret"],
    }


@responses.activate
def test_provider_uses_explicit_token_url_without_discovery():
    responses.add(responses.POST, TOKEN_URL, json=_token("abc123"), status=200)

    assert _provider(token_url=TOKEN_URL).get_token() == "abc123"
    assert [c.request.url for c in responses.calls] == [TOKEN_URL]


@responses.activate
def test_provider_caches_the_token_and_the_endpoint():
    responses.add(
        responses.GET, DISCOVERY_URL, json={"token_endpoint": TOKEN_URL}, status=200
    )
    responses.add(responses.POST, TOKEN_URL, json=_token("first"), status=200)
    responses.add(responses.POST, TOKEN_URL, json=_token("second"), status=200)
    provider = _provider()

    assert provider.get_token() == "first"
    assert provider.get_token() == "first"  # served from cache
    provider.invalidate()
    assert provider.get_token() == "second"
    assert len(responses.calls) == 3  # one discovery, two token requests


@responses.activate
def test_provider_renews_after_80_percent_of_the_lifetime(monkeypatch):
    now = [1000.0]
    monkeypatch.setattr("wattnet.client.auth.time.monotonic", lambda: now[0])
    responses.add(responses.POST, TOKEN_URL, json=_token("first", 3600), status=200)
    responses.add(responses.POST, TOKEN_URL, json=_token("second", 3600), status=200)
    provider = _provider(token_url=TOKEN_URL)

    assert provider.get_token() == "first"
    now[0] += 2879
    assert provider.get_token() == "first"
    now[0] += 2
    assert provider.get_token() == "second"


@responses.activate
@pytest.mark.parametrize("status", [400, 401])
def test_provider_invalid_credentials(status):
    responses.add(
        responses.POST,
        TOKEN_URL,
        json={"error": "invalid_client", "error_description": "Invalid secret"},
        status=status,
    )

    with pytest.raises(AuthenticationError, match="Invalid secret"):
        _provider(token_url=TOKEN_URL).get_token()


@responses.activate
def test_provider_upstream_failure():
    responses.add(responses.POST, TOKEN_URL, json={"detail": "boom"}, status=500)

    with pytest.raises(WattnetAPIError) as exc_info:
        _provider(token_url=TOKEN_URL).get_token()
    assert exc_info.value.status_code == 500


@responses.activate
def test_provider_rejects_a_response_without_a_token():
    responses.add(responses.POST, TOKEN_URL, json={"token_type": "Bearer"}, status=200)

    with pytest.raises(WattnetError, match="Unexpected response"):
        _provider(token_url=TOKEN_URL).get_token()


@responses.activate
def test_provider_retries_transient_network_errors():
    responses.add(
        responses.POST, TOKEN_URL, body=requests.exceptions.ConnectionError("boom")
    )
    responses.add(responses.POST, TOKEN_URL, json=_token("abc123"), status=200)

    assert _provider(token_url=TOKEN_URL, retry_count=2).get_token() == "abc123"
    assert len(responses.calls) == 2


@responses.activate
def test_provider_rejects_a_discovery_document_without_a_token_endpoint():
    responses.add(responses.GET, DISCOVERY_URL, json={"issuer": ISSUER_URL})

    with pytest.raises(WattnetError, match="token_endpoint"):
        _provider().get_token()
