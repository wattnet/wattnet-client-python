"""Tests for AsyncWattnetRawClient and the async auth providers.

They run against a real local `aiohttp` server whose responses are queued per
test, so the whole HTTP stack (query serialization, headers, retries) is
exercised without any mocking library.
"""

import asyncio
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import aiohttp
import pytest

from wattnet.client import AsyncWattnetRawClient, async_register
from wattnet.client.async_auth import AsyncCredentialsTokenProvider
from wattnet.client.exceptions import (
    AuthenticationError,
    ConfigurationError,
    WattnetAPIError,
)

from ..conftest import TOKEN


def _expires(minutes: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()


def _token(name: str, minutes: int = 30) -> Dict[str, str]:
    return {"access_token": name, "expires_at": _expires(minutes)}


# -- construction ---------------------------------------------------------


def test_constructor_rejects_token_and_credentials_together():
    with pytest.raises(ConfigurationError):
        AsyncWattnetRawClient(token="t", email="e@example.com", password="p")


def test_constructor_requires_some_auth():
    with pytest.raises(ConfigurationError):
        AsyncWattnetRawClient()


def test_constructor_requires_both_email_and_password():
    with pytest.raises(ConfigurationError):
        AsyncWattnetRawClient(email="e@example.com")


def test_repr_hides_credentials():
    client = AsyncWattnetRawClient(email="e@example.com", password="secret")
    assert "secret" not in repr(client)
    assert "AsyncCredentialsTokenProvider" in repr(client)


def test_async_client_does_not_import_pandas():
    code = (
        "import sys; import wattnet.client; "
        "from wattnet.client import AsyncWattnetRawClient, WattnetRawClient; "
        "assert 'pandas' not in sys.modules"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


# -- requests -------------------------------------------------------------


async def test_sends_bearer_token_and_query_params(server, make_client):
    server.add("GET", "/v1/generation", json=[])
    async with make_client() as client:
        assert await client.get_generation(zone="es", production_type="solar") == []

    (call,) = server.calls("GET", "/v1/generation")
    assert call.headers["Authorization"] == f"Bearer {TOKEN}"
    assert call.query["zone"] == "es"
    assert call.query["production_type"] == "solar"


async def test_serializes_datetimes_and_bools(server, make_client):
    server.add("GET", "/v1/footprints", json=[])
    async with make_client() as client:
        await client.get_footprints(
            zone="ES",
            start=datetime(2026, 1, 1),
            end=datetime(2026, 1, 2),
            aggregate=True,
        )

    (call,) = server.calls("GET", "/v1/footprints")
    assert call.query["start"] == "2026-01-01T00:00:00+00:00"
    assert call.query["end"] == "2026-01-02T00:00:00+00:00"
    assert call.query["aggregate"] == "true"
    assert "lat" not in call.query


async def test_returns_parsed_json(server, make_client, zones_payload):
    server.add("GET", "/v1/zones", json=zones_payload)
    async with make_client() as client:
        assert await client.get_zones() == zones_payload


async def test_zones_are_cached(server, make_client, zones_payload):
    server.add("GET", "/v1/zones", json=zones_payload)
    async with make_client() as client:
        await client.get_zones()
        await client.get_zones()
    assert len(server.calls("GET", "/v1/zones")) == 1


async def test_raises_wattnet_api_error_on_4xx(server, make_client):
    server.add(
        "GET", "/v1/generation", status=422, json={"detail": "Invalid input parameters"}
    )
    async with make_client() as client:
        with pytest.raises(WattnetAPIError) as exc:
            await client.get_generation(zone="XX")
    assert exc.value.status_code == 422
    assert exc.value.detail == "Invalid input parameters"


async def test_non_json_error_body_becomes_detail(server, make_client):
    server.add("GET", "/v1/status", status=404, text="Not found")
    async with make_client() as client:
        with pytest.raises(WattnetAPIError) as exc:
            await client.get_status()
    assert exc.value.status_code == 404
    assert exc.value.detail == "Not found"


# -- retries --------------------------------------------------------------


async def test_retries_5xx_then_succeeds(server, make_client):
    server.add("GET", "/v1/status", status=503, json={"detail": "down"})
    server.add("GET", "/v1/status", json={"status": "ok"})
    async with make_client() as client:
        assert await client.get_status() == {"status": "ok"}
    assert len(server.calls("GET", "/v1/status")) == 2


async def test_gives_up_after_retry_count(server, make_client):
    server.add("GET", "/v1/status", status=503, json={"detail": "down"})
    async with make_client(retry_count=2) as client:
        with pytest.raises(WattnetAPIError) as exc:
            await client.get_status()
    assert exc.value.status_code == 503
    assert len(server.calls("GET", "/v1/status")) == 3


async def test_429_honours_retry_after(server, make_client, monkeypatch):
    sleeps: List[float] = []
    real_sleep = asyncio.sleep

    async def fake_sleep(seconds):
        sleeps.append(seconds)
        await real_sleep(0)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    server.add("GET", "/v1/status", status=429, json={}, headers={"Retry-After": "7"})
    server.add("GET", "/v1/status", json={"status": "ok"})
    async with make_client() as client:
        await client.get_status()
    assert sleeps == [7.0]


async def test_retries_connection_errors(server, make_client):
    server.drop("GET", "/v1/status")
    server.add("GET", "/v1/status", json={"status": "ok"})
    async with make_client() as client:
        assert await client.get_status() == {"status": "ok"}


async def test_connection_error_raised_when_retries_exhausted(server, make_client):
    server.drop("GET", "/v1/status")
    async with make_client(retry_count=0) as client:
        with pytest.raises(aiohttp.ClientConnectionError):
            await client.get_status()


async def test_401_refreshes_token_once(server, make_client):
    server.add("POST", "/token-request/get_token", json=_token("old"))
    server.add("POST", "/token-request/get_token", json=_token("new"))
    server.add("GET", "/v1/status", status=401, json={"detail": "expired"})
    server.add("GET", "/v1/status", json={"status": "ok"})
    async with make_client(email="e@x.com", password="p") as client:
        assert await client.get_status() == {"status": "ok"}
    sent = [c.headers["Authorization"] for c in server.calls("GET", "/v1/status")]
    assert sent == ["Bearer old", "Bearer new"]


# -- session handling -----------------------------------------------------


async def test_uses_and_does_not_close_supplied_session(server, make_client):
    server.add("GET", "/v1/status", json={"status": "ok"})
    async with aiohttp.ClientSession() as session:
        client = make_client(session=session)
        await client.get_status()
        await client.close()
        assert not session.closed


async def test_closes_owned_session(server, make_client):
    server.add("GET", "/v1/status", json={"status": "ok"})
    client = make_client()
    await client.get_status()
    session = client._session
    await client.close()
    assert session.closed


# -- auth -----------------------------------------------------------------


async def test_credentials_provider_caches_token(server):
    server.add("POST", "/token-request/get_token", json=_token("tok"))
    async with aiohttp.ClientSession() as session:
        provider = AsyncCredentialsTokenProvider(
            "e@x.com", "p", server.token_url, session
        )
        assert await provider.get_token() == "tok"
        assert await provider.get_token() == "tok"
    assert len(server.calls("POST", "/token-request/get_token")) == 1


async def test_credentials_provider_refetches_after_expiry_and_invalidate(server):
    server.add("POST", "/token-request/get_token", json=_token("a", minutes=0))
    server.add("POST", "/token-request/get_token", json=_token("b"))
    server.add("POST", "/token-request/get_token", json=_token("c"))
    async with aiohttp.ClientSession() as session:
        provider = AsyncCredentialsTokenProvider(
            "e@x.com", "p", server.token_url, session
        )
        assert await provider.get_token() == "a"  # already inside safety margin
        assert await provider.get_token() == "b"
        provider.invalidate()
        assert await provider.get_token() == "c"


async def test_credentials_provider_parses_z_suffix(server):
    server.add(
        "POST",
        "/token-request/get_token",
        json={"access_token": "t", "expires_at": "2999-01-01T00:00:00.123456Z"},
    )
    async with aiohttp.ClientSession() as session:
        provider = AsyncCredentialsTokenProvider(
            "e@x.com", "p", server.token_url, session
        )
        assert await provider.get_token() == "t"


async def test_credentials_provider_invalid_credentials(server):
    server.add(
        "POST",
        "/token-request/get_token",
        status=401,
        json={"detail": "bad credentials"},
    )
    async with aiohttp.ClientSession() as session:
        provider = AsyncCredentialsTokenProvider(
            "e@x.com", "p", server.token_url, session
        )
        with pytest.raises(AuthenticationError, match="bad credentials"):
            await provider.get_token()


async def test_credentials_provider_upstream_failure(server):
    server.add(
        "POST", "/token-request/get_token", status=502, json={"detail": "bad gw"}
    )
    async with aiohttp.ClientSession() as session:
        provider = AsyncCredentialsTokenProvider(
            "e@x.com", "p", server.token_url, session, retry_count=0
        )
        with pytest.raises(WattnetAPIError) as exc:
            await provider.get_token()
    assert exc.value.status_code == 502


async def test_credentials_provider_retries_connection_error(server):
    server.drop("POST", "/token-request/get_token")
    server.add("POST", "/token-request/get_token", json=_token("tok"))
    async with aiohttp.ClientSession() as session:
        provider = AsyncCredentialsTokenProvider(
            "e@x.com", "p", server.token_url, session, retry_delay=0
        )
        assert await provider.get_token() == "tok"


async def test_async_register_returns_message(server):
    server.add(
        "POST",
        "/token-request/register",
        json={"message": "User registered successfully."},
    )
    message = await async_register("e@x.com", "p", token_url=server.token_url)
    assert message == "User registered successfully."


async def test_async_register_not_authorized(server):
    server.add(
        "POST", "/token-request/register", status=403, json={"detail": "not allowed"}
    )
    with pytest.raises(AuthenticationError, match="not allowed"):
        await async_register("e@x.com", "p", token_url=server.token_url)
