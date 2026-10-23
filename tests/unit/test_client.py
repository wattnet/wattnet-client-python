"""End-to-end tests for WattnetRawClient/WattnetClient against a mocked API."""

import pandas as pd
import pytest
import requests
import responses

from wattnet.client import WattnetClient, WattnetRawClient
from wattnet.client.exceptions import ConfigurationError, WattnetAPIError

from ..conftest import BASE_URL, TOKEN, TOKEN_URL


def test_constructor_rejects_token_and_credentials_together():
    with pytest.raises(ConfigurationError):
        WattnetRawClient(token="t", client_id="id", client_secret="s")


def test_constructor_requires_some_auth():
    with pytest.raises(ConfigurationError):
        WattnetRawClient()


def test_constructor_requires_both_client_id_and_secret():
    with pytest.raises(ConfigurationError):
        WattnetRawClient(client_id="id")


@responses.activate
def test_raw_client_sends_bearer_token_and_query_params(raw_client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/generation",
        json=[],
        status=200,
    )

    raw_client.get_generation(zone="es", production_type="solar")

    request = responses.calls[0].request
    assert request.headers["Authorization"] == f"Bearer {TOKEN}"
    assert "zone=es" in request.url
    assert "production_type=solar" in request.url


@responses.activate
def test_raw_client_returns_parsed_json(raw_client, zones_payload):
    responses.add(responses.GET, f"{BASE_URL}/zones", json=zones_payload, status=200)

    result = raw_client.get_zones()

    assert result == zones_payload


@responses.activate
def test_raw_client_raises_wattnet_api_error_on_4xx(raw_client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/generation",
        json={"detail": "Invalid input parameters"},
        status=400,
    )

    with pytest.raises(WattnetAPIError) as exc_info:
        raw_client.get_generation(zone="XX")
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid input parameters"


@responses.activate
def test_client_returns_dataframe(client, generation_payload):
    responses.add(
        responses.GET, f"{BASE_URL}/generation", json=generation_payload, status=200
    )

    df = client.get_generation(zone="ES")

    assert isinstance(df, pd.DataFrame)
    assert set(df["production_type"]) == {"solar", "wind_onshore"}


@responses.activate
def test_client_status_is_a_one_row_dataframe(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/status",
        json={"storage": "up", "entso-e": "up", "elexon": "down", "epias": "up"},
        status=200,
    )

    df = client.get_status()

    assert len(df) == 1
    assert df.iloc[0]["elexon"] == "down"


@responses.activate
def test_client_refreshes_token_once_on_401_then_succeeds():
    responses.add(
        responses.POST,
        TOKEN_URL,
        json={
            "access_token": "first",
            "expires_in": 3600,
        },
        status=200,
    )
    responses.add(
        responses.POST,
        TOKEN_URL,
        json={
            "access_token": "second",
            "expires_in": 3600,
        },
        status=200,
    )
    responses.add(
        responses.GET, f"{BASE_URL}/zones", json={"detail": "expired"}, status=401
    )
    responses.add(responses.GET, f"{BASE_URL}/zones", json=[], status=200)

    client = WattnetClient(
        client_id="id",
        client_secret="secret",
        base_url=BASE_URL,
        token_url=TOKEN_URL,
    )
    df = client.get_zones()

    assert isinstance(df, pd.DataFrame)
    # calls: [0] POST get_token -> "first", [1] GET /zones (401, Bearer first),
    # [2] POST get_token -> "second", [3] GET /zones (200, Bearer second)
    assert responses.calls[1].request.headers["Authorization"] == "Bearer first"
    assert responses.calls[3].request.headers["Authorization"] == "Bearer second"


@responses.activate
def test_raw_client_retries_on_503_then_succeeds(raw_client, monkeypatch):
    sleeps = []
    monkeypatch.setattr("wattnet.client.raw_client.time.sleep", sleeps.append)
    responses.add(responses.GET, f"{BASE_URL}/zones", status=503)
    responses.add(responses.GET, f"{BASE_URL}/zones", json=[], status=200)

    result = raw_client.get_zones()

    assert result == []
    assert len(responses.calls) == 2
    assert sleeps == [raw_client._retry_delay]


@responses.activate
def test_raw_client_honors_retry_after_header_on_429(raw_client, monkeypatch):
    sleeps = []
    monkeypatch.setattr("wattnet.client.raw_client.time.sleep", sleeps.append)
    responses.add(
        responses.GET,
        f"{BASE_URL}/generation",
        status=429,
        headers={"Retry-After": "5"},
    )
    responses.add(responses.GET, f"{BASE_URL}/generation", json=[], status=200)

    raw_client.get_generation(zone="ES")

    assert sleeps == [5.0]


@responses.activate
def test_raw_client_retries_on_connection_error_then_succeeds(raw_client, monkeypatch):
    sleeps = []
    monkeypatch.setattr("wattnet.client.raw_client.time.sleep", sleeps.append)
    responses.add(
        responses.GET,
        f"{BASE_URL}/zones",
        body=requests.exceptions.ConnectionError("boom"),
    )
    responses.add(responses.GET, f"{BASE_URL}/zones", json=[], status=200)

    result = raw_client.get_zones()

    assert result == []
    assert len(responses.calls) == 2
    assert sleeps == [raw_client._retry_delay]


@responses.activate
def test_raw_client_gives_up_after_exhausting_retries_on_persistent_connection_errors(
    raw_client, monkeypatch
):
    monkeypatch.setattr("wattnet.client.raw_client.time.sleep", lambda s: None)
    for _ in range(raw_client._retry_count + 1):
        responses.add(
            responses.GET,
            f"{BASE_URL}/zones",
            body=requests.exceptions.ConnectionError("boom"),
        )

    with pytest.raises(requests.exceptions.ConnectionError):
        raw_client.get_zones()

    assert len(responses.calls) == raw_client._retry_count + 1


@responses.activate
def test_raw_client_falls_back_to_default_delay_for_non_numeric_retry_after(
    raw_client, monkeypatch
):
    sleeps = []
    monkeypatch.setattr("wattnet.client.raw_client.time.sleep", sleeps.append)
    responses.add(
        responses.GET,
        f"{BASE_URL}/generation",
        status=429,
        headers={"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"},
    )
    responses.add(responses.GET, f"{BASE_URL}/generation", json=[], status=200)

    raw_client.get_generation(zone="ES")

    assert sleeps == [raw_client._retry_delay]


@responses.activate
def test_raw_client_does_not_retry_non_retryable_4xx(raw_client, monkeypatch):
    sleeps = []
    monkeypatch.setattr("wattnet.client.raw_client.time.sleep", sleeps.append)
    responses.add(
        responses.GET, f"{BASE_URL}/generation", json={"detail": "bad"}, status=400
    )

    with pytest.raises(WattnetAPIError):
        raw_client.get_generation(zone="ES")

    assert sleeps == []
    assert len(responses.calls) == 1


@responses.activate
def test_raw_client_gives_up_after_exhausting_retries_on_persistent_5xx(
    raw_client, monkeypatch
):
    monkeypatch.setattr("wattnet.client.raw_client.time.sleep", lambda s: None)
    for _ in range(raw_client._retry_count + 1):
        responses.add(responses.GET, f"{BASE_URL}/generation", status=503)

    with pytest.raises(WattnetAPIError) as exc_info:
        raw_client.get_generation(zone="ES")

    assert exc_info.value.status_code == 503
    assert len(responses.calls) == raw_client._retry_count + 1


@responses.activate
def test_raw_client_caches_get_zones(raw_client, zones_payload):
    responses.add(responses.GET, f"{BASE_URL}/zones", json=zones_payload, status=200)

    first = raw_client.get_zones()
    second = raw_client.get_zones()

    assert first == second == zones_payload
    assert len(responses.calls) == 1


@responses.activate
def test_raw_client_caches_get_factors_per_argument_combination(raw_client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/factors",
        json=[{"factor_type": "carbon"}],
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE_URL}/factors",
        json=[{"factor_type": "water"}],
        status=200,
    )

    carbon_first = raw_client.get_factors(factor_type="carbon")
    carbon_second = raw_client.get_factors(factor_type="carbon")
    water = raw_client.get_factors(factor_type="water")

    assert carbon_first == carbon_second == [{"factor_type": "carbon"}]
    assert water == [{"factor_type": "water"}]
    assert len(responses.calls) == 2


def _series_payload(block_key=None):
    series_item = {"valid": True, "zone_status": "complete"}
    if block_key:
        series_item[block_key] = [{"values": [["2026-01-01T00:00:00Z", 1.0]]}]
    else:
        series_item["values"] = [["2026-01-01T00:00:00Z", 1.0]]
    return [{"zone": "ES", "series": [series_item]}]


# (method name, path, kwargs, block_key used by @dataframe, or None if flat/record)
CLIENT_METHODS = [
    ("get_load", "/load", {"zone": "ES"}, None),
    ("get_imports", "/imports", {"zone": "ES"}, "imports"),
    ("get_exports", "/exports", {"zone": "ES"}, "exports"),
    ("get_mix", "/mix", {"zone": "ES"}, "production"),
    ("get_footprints", "/footprints", {"zone": "ES"}, None),
    ("get_impacts", "/impacts", {"zone": "ES"}, None),
    ("get_environmental_score", "/environmental-score", {"zone": "ES"}, None),
    ("get_flow_share", "/flow-share", {"zone": "ES"}, "flows"),
    ("get_mix_share", "/mix-share", {"zone": "ES"}, "shares"),
    ("get_footprint_share", "/footprint-share", {"zone": "ES"}, "blocks"),
    ("get_impact_share", "/impact-share", {"zone": "ES"}, "blocks"),
    ("get_factors", "/factors", {}, None),
]


@responses.activate
@pytest.mark.parametrize("method_name, path, kwargs, block_key", CLIENT_METHODS)
def test_client_method_returns_dataframe(client, method_name, path, kwargs, block_key):
    responses.add(
        responses.GET,
        f"{BASE_URL}{path}",
        json=_series_payload(block_key),
        status=200,
    )

    df = getattr(client, method_name)(**kwargs)

    assert isinstance(df, pd.DataFrame)
    assert list(df["value"]) == [1.0]


STATUS_METHODS = [
    ("get_status_storage", "/status/storage", "storage"),
    ("get_status_entsoe", "/status/entso-e", "entso-e"),
    ("get_status_elexon", "/status/elexon", "elexon"),
    ("get_status_epias", "/status/epias", "epias"),
]


@responses.activate
@pytest.mark.parametrize("method_name, path, key", STATUS_METHODS)
def test_client_status_variant_is_a_one_row_dataframe(client, method_name, path, key):
    responses.add(responses.GET, f"{BASE_URL}{path}", json={key: "up"}, status=200)

    df = getattr(client, method_name)()

    assert len(df) == 1
    assert df.iloc[0][key] == "up"


def test_repr_shows_base_url_and_auth_mode_but_never_the_token():
    text = repr(WattnetClient(token="super-secret-token", base_url=BASE_URL))

    assert "WattnetClient" in text
    assert BASE_URL in text
    assert "StaticTokenProvider" in text
    assert "super-secret-token" not in text


def test_close_closes_the_underlying_session():
    client = WattnetClient(token=TOKEN, base_url=BASE_URL)
    closed = []
    client._session.close = lambda: closed.append(True)

    client.close()

    assert closed == [True]


def test_context_manager_closes_session_on_exit():
    closed = []
    with WattnetClient(token=TOKEN, base_url=BASE_URL) as client:
        client._session.close = lambda: closed.append(True)
        assert closed == []

    assert closed == [True]
