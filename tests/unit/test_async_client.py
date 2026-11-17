"""Tests for AsyncWattnetRawClient and the async auth providers.

They run against a real local `aiohttp` server whose responses are queued per
test, so the whole HTTP stack (query serialization, headers, retries) is
exercised without any mocking library.
"""

import asyncio
import subprocess
import sys
from datetime import datetime
from typing import Dict, List

import aiohttp
import pytest

from wattnet.client import AsyncWattnetRawClient
from wattnet.client.async_auth import AsyncClientCredentialsTokenProvider
from wattnet.client.exceptions import (
    AuthenticationError,
    ConfigurationError,
    WattnetAPIError,
)

from ..conftest import TOKEN


def _token(name: str, expires_in: int = 3600) -> Dict[str, object]:
    return {"access_token": name, "expires_in": expires_in, "token_type": "Bearer"}


# -- construction ---------------------------------------------------------


def test_constructor_rejects_token_and_credentials_together():
    with pytest.raises(ConfigurationError):
        AsyncWattnetRawClient(token="t", client_id="id", client_secret="s")


def test_constructor_requires_some_auth():
    with pytest.raises(ConfigurationError):
        AsyncWattnetRawClient()


def test_constructor_requires_both_client_id_and_secret():
    with pytest.raises(ConfigurationError):
        AsyncWattnetRawClient(client_id="id")


def test_repr_hides_credentials():
    client = AsyncWattnetRawClient(client_id="id", client_secret="secret")
    assert "secret" not in repr(client)
    assert "AsyncClientCredentialsTokenProvider" in repr(client)


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
    # aiohttp itself replays a request once when a connection drops, so two drops
    # are needed for the error to reach the client's own retry.
    server.drop("GET", "/v1/status")
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
    server.add("POST", "/token", json=_token("old"))
    server.add("POST", "/token", json=_token("new"))
    server.add("GET", "/v1/status", status=401, json={"detail": "expired"})
    server.add("GET", "/v1/status", json={"status": "ok"})
    async with make_client(client_id="id", client_secret="s") as client:
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


def _provider(session, server, **kwargs):
    kwargs.setdefault("token_url", server.token_url)
    kwargs.setdefault("retry_delay", 0)
    return AsyncClientCredentialsTokenProvider(
        "id", "s3cret", f"{server.base_url}/issuer", session=session, **kwargs
    )


async def test_provider_caches_token_and_sends_the_grant(server):
    server.add("POST", "/token", json=_token("tok"))
    async with aiohttp.ClientSession() as session:
        provider = _provider(session, server)
        assert await provider.get_token() == "tok"
        assert await provider.get_token() == "tok"
    calls = server.calls("POST", "/token")
    assert len(calls) == 1
    assert await calls[0].post() == {
        "grant_type": "client_credentials",
        "client_id": "id",
        "client_secret": "s3cret",
    }


async def test_provider_discovers_token_endpoint(server):
    server.add(
        "GET",
        "/v1/issuer/.well-known/openid-configuration",
        json={"token_endpoint": server.token_url},
    )
    server.add("POST", "/token", json=_token("a"))
    server.add("POST", "/token", json=_token("b"))
    async with aiohttp.ClientSession() as session:
        provider = _provider(session, server, token_url=None)
        assert await provider.get_token() == "a"
        provider.invalidate()
        assert await provider.get_token() == "b"
    assert len(server.calls("GET", "/v1/issuer/.well-known/openid-configuration")) == 1


async def test_provider_renews_after_80_percent_of_the_lifetime(server, monkeypatch):
    now = [1000.0]
    monkeypatch.setattr("wattnet.client.async_auth.time.monotonic", lambda: now[0])
    server.add("POST", "/token", json=_token("a", 3600))
    server.add("POST", "/token", json=_token("b", 3600))
    async with aiohttp.ClientSession() as session:
        provider = _provider(session, server)
        assert await provider.get_token() == "a"
        now[0] += 2879
        assert await provider.get_token() == "a"
        now[0] += 2
        assert await provider.get_token() == "b"


async def test_provider_invalid_credentials(server):
    server.add(
        "POST",
        "/token",
        status=401,
        json={"error": "invalid_client", "error_description": "Invalid secret"},
    )
    async with aiohttp.ClientSession() as session:
        with pytest.raises(AuthenticationError, match="Invalid secret"):
            await _provider(session, server).get_token()


async def test_provider_upstream_failure(server):
    server.add("POST", "/token", status=502, json={"detail": "bad gw"})
    async with aiohttp.ClientSession() as session:
        with pytest.raises(WattnetAPIError) as exc:
            await _provider(session, server, retry_count=0).get_token()
    assert exc.value.status_code == 502


async def test_provider_retries_connection_error(server):
    server.drop("POST", "/token")
    server.add("POST", "/token", json=_token("tok"))
    async with aiohttp.ClientSession() as session:
        assert await _provider(session, server).get_token() == "tok"


async def test_provider_gives_up_on_connection_error_after_retries(server):
    server.drop("POST", "/token")
    async with aiohttp.ClientSession() as session:
        with pytest.raises(aiohttp.ClientConnectionError):
            await _provider(session, server, retry_count=0).get_token()


async def test_resolution_is_sent_only_when_given(server, make_client):
    server.add("GET", "/v1/load", json=[])
    async with make_client() as client:
        await client.get_load(zone="ES")
        await client.get_load(zone="ES", resolution="1h")
    first, second = server.calls("GET", "/v1/load")
    assert "resolution" not in first.query
    assert second.query["resolution"] == "1h"


async def test_answers_are_asked_compressed_unless_told_otherwise(server, make_client):
    server.add("GET", "/v1/load", json=[])
    async with make_client() as client:
        await client.get_load()
    async with make_client(compress=False) as client:
        await client.get_load()
    default, plain = server.calls("GET", "/v1/load")
    assert "gzip" in default.headers["Accept-Encoding"]
    assert plain.headers["Accept-Encoding"] == "identity"


async def test_api_error_carries_the_stable_code(server, make_client):
    server.add(
        "GET",
        "/v1/load",
        status=400,
        json={"detail": "Invalid resolution '7m'.", "code": "invalid_resolution"},
    )
    server.add("GET", "/v1/zones", status=400, json={"detail": "nope"})
    async with make_client() as client:
        with pytest.raises(WattnetAPIError) as exc:
            await client.get_load(resolution="7m")
        assert exc.value.code == "invalid_resolution"
        assert exc.value.detail == "Invalid resolution '7m'."
        with pytest.raises(WattnetAPIError) as exc:
            await client.get_zones()
        assert exc.value.code is None
