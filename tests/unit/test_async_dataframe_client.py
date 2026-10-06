"""Tests for AsyncWattnetClient, the async DataFrame client."""

import pandas as pd
import pytest

from wattnet.client import AsyncWattnetClient
from wattnet.client.exceptions import WattnetAPIError


def _series_payload(block_key=None):
    series_item = {"valid": True, "zone_status": "complete"}
    if block_key:
        series_item[block_key] = [{"values": [["2026-01-01T00:00:00Z", 1.0]]}]
    else:
        series_item["values"] = [["2026-01-01T00:00:00Z", 1.0]]
    return [{"zone": "ES", "series": [series_item]}]


@pytest.fixture
def make_df_client(server):
    def factory(**kwargs):
        return AsyncWattnetClient(
            token="test-token",
            base_url=server.base_url,
            token_url=server.token_url,
            retry_delay=0,
            **kwargs,
        )

    return factory


async def test_get_generation_returns_dataframe(server, make_df_client):
    payload = [
        {
            "zone": "ES",
            "unit": "MW",
            "series": [
                {
                    "valid": True,
                    "zone_status": "complete",
                    "production": [
                        {
                            "production_type": "solar",
                            "data_state": "official",
                            "datasource": "ENTSO-E",
                            "values": [["2026-01-01T00:00:00Z", 12.5]],
                        }
                    ],
                }
            ],
        }
    ]
    server.add("GET", "/v1/generation", json=payload)
    async with make_df_client() as client:
        df = await client.get_generation(zone="ES")

    assert isinstance(df, pd.DataFrame)
    assert list(df["value"]) == [12.5]
    assert df.loc[0, "production_type"] == "solar"
    assert df.loc[0, "valid"]
    assert str(df["timestamp"].dtype) == "datetime64[ns, UTC]"


async def test_get_zones_returns_dataframe(server, make_df_client, zones_payload):
    server.add("GET", "/v1/zones", json=zones_payload)
    async with make_df_client() as client:
        df = await client.get_zones()
        again = await client.get_zones()
    assert list(df["zone"]) == [z["zone"] for z in zones_payload]
    assert df.equals(again)
    assert len(server.calls("GET", "/v1/zones")) == 1  # cached raw JSON


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


@pytest.mark.parametrize("method_name, path, kwargs, block_key", CLIENT_METHODS)
async def test_method_returns_dataframe(
    server, make_df_client, method_name, path, kwargs, block_key
):
    server.add("GET", f"/v1{path}", json=_series_payload(block_key))
    async with make_df_client() as client:
        df = await getattr(client, method_name)(**kwargs)

    assert isinstance(df, pd.DataFrame)
    assert list(df["value"]) == [1.0]


STATUS_METHODS = [
    ("get_status_storage", "/status/storage", "storage"),
    ("get_status_entsoe", "/status/entso-e", "entso-e"),
    ("get_status_elexon", "/status/elexon", "elexon"),
    ("get_status_epias", "/status/epias", "epias"),
]


@pytest.mark.parametrize("method_name, path, key", STATUS_METHODS)
async def test_status_variant_is_a_one_row_dataframe(
    server, make_df_client, method_name, path, key
):
    server.add("GET", f"/v1{path}", json={key: "up"})
    async with make_df_client() as client:
        df = await getattr(client, method_name)()

    assert len(df) == 1
    assert df.iloc[0][key] == "up"


async def test_get_status_is_a_one_row_dataframe(server, make_df_client):
    server.add("GET", "/v1/status", json={"api": "up"})
    async with make_df_client() as client:
        df = await client.get_status()
    assert df.iloc[0]["api"] == "up"


async def test_api_errors_propagate(server, make_df_client):
    server.add("GET", "/v1/load", status=422, json={"detail": "bad zone"})
    async with make_df_client() as client:
        with pytest.raises(WattnetAPIError):
            await client.get_load(zone="XX")


def test_repr_shows_class_and_hides_token(server, make_df_client):
    text = repr(make_df_client())
    assert "AsyncWattnetClient" in text
    assert "test-token" not in text
