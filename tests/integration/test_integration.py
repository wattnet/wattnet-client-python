"""Integration tests against a real, running wattnet-api instance.

Skipped unless `WATTNET_TEST_BASE_URL` and `WATTNET_TEST_TOKEN` are set in
the environment — these tests make real HTTP calls and are not run by
default in CI. Example local setup:

    export WATTNET_TEST_BASE_URL=http://localhost:8000/v1
    export WATTNET_TEST_TOKEN=<a valid bearer token>
    pytest tests/integration -v
"""

import os

import pandas as pd
import pytest

from wattnet.client import WattnetClient

BASE_URL = os.environ.get("WATTNET_TEST_BASE_URL")
TOKEN = os.environ.get("WATTNET_TEST_TOKEN")

pytestmark = pytest.mark.integration

requires_live_api = pytest.mark.skipif(
    not (BASE_URL and TOKEN),
    reason="WATTNET_TEST_BASE_URL and WATTNET_TEST_TOKEN must be set",
)


@pytest.fixture
def live_client() -> WattnetClient:
    return WattnetClient(token=TOKEN, base_url=BASE_URL)


@requires_live_api
def test_get_zones_returns_a_non_empty_dataframe(live_client):
    df = live_client.get_zones()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "zone" in df.columns


@requires_live_api
def test_get_generation_for_a_known_zone(live_client):
    zones = live_client.get_zones()
    zone = zones.iloc[0]["zone"]

    df = live_client.get_generation(zone=zone)

    assert isinstance(df, pd.DataFrame)


@requires_live_api
def test_get_status_reports_all_dependencies(live_client):
    df = live_client.get_status()

    assert not df.empty
    assert {"storage", "entso-e", "elexon", "epias"}.issubset(df.columns)
