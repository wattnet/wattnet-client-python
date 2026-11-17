"""Shared fixtures for wattnet-client tests."""

import pytest

from wattnet.client import WattnetClient, WattnetRawClient

BASE_URL = "https://wattnet-api.test/v1"
TOKEN_URL = "https://auth.wattnet.test/token"
TOKEN = "test-token"


@pytest.fixture
def raw_client() -> WattnetRawClient:
    """A `WattnetRawClient` authenticated with a fixed test token."""
    return WattnetRawClient(token=TOKEN, base_url=BASE_URL, token_url=TOKEN_URL)


@pytest.fixture
def client() -> WattnetClient:
    """A `WattnetClient` authenticated with a fixed test token."""
    return WattnetClient(token=TOKEN, base_url=BASE_URL, token_url=TOKEN_URL)


@pytest.fixture
def generation_payload():
    """Sample `/generation` payload: zone -> series -> production blocks -> values."""
    return [
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
                            "points": [
                                {
                                    "timestamp": "2026-01-01T00:00:00+00:00",
                                    "value": 100.0,
                                    "updated_at": "2026-01-02T03:04:05+00:00",
                                },
                                {
                                    "timestamp": "2026-01-01T01:00:00+00:00",
                                    "value": 110.0,
                                    "updated_at": "2026-01-02T03:04:05+00:00",
                                },
                            ],
                        },
                        {
                            "production_type": "wind_onshore",
                            "data_state": "official",
                            "datasource": "ENTSO-E",
                            "points": [
                                {
                                    "timestamp": "2026-01-01T00:00:00+00:00",
                                    "value": 200.0,
                                    "updated_at": "2026-01-02T03:04:05+00:00",
                                },
                                {
                                    "timestamp": "2026-01-01T01:00:00+00:00",
                                    "value": 190.0,
                                    "updated_at": "2026-01-02T03:04:05+00:00",
                                },
                            ],
                        },
                    ],
                }
            ],
        }
    ]


@pytest.fixture
def footprints_payload():
    """Sample non-aggregate `/footprints` payload: zone -> series -> values."""
    return [
        {
            "footprint_type": "carbon",
            "scope": "life-cycle",
            "zone": "ES",
            "unit": "gCO2eq/kWh",
            "coverage": 1.0,
            "series": [
                {
                    "valid": True,
                    "zone_status": "complete",
                    "points": [
                        {
                            "timestamp": "2026-01-01T00:00:00+00:00",
                            "value": 150.0,
                            "updated_at": "2026-01-02T03:04:05+00:00",
                        },
                        {
                            "timestamp": "2026-01-01T01:00:00+00:00",
                            "value": 145.0,
                            "updated_at": "2026-01-02T03:04:05+00:00",
                        },
                    ],
                }
            ],
        }
    ]


@pytest.fixture
def footprints_aggregate_payload():
    """Sample `/footprints?aggregate=true` payload: already-flat records."""
    return [
        {
            "footprint_type": "carbon",
            "scope": "life-cycle",
            "zone": "ES",
            "unit": "gCO2eq/kWh",
            "coverage": 1.0,
            "start": "2026-01-01T00:00:00+00:00",
            "end": "2026-01-02T00:00:00+00:00",
            "value": 148.0,
            "valid": True,
            "zone_status": "complete",
            "aggregation_method": "mean",
        }
    ]


@pytest.fixture
def zones_payload():
    """Sample `/zones` payload: flat records, no `series`."""
    return [
        {
            "zone": "ES",
            "full_name": "Spain",
            "eic_code": "10YES-REE------0",
            "country_code": "ES",
            "country_name": "Spain",
            "provider": "ENTSO-E",
            "neighbours": ["FR", "PT"],
        }
    ]
