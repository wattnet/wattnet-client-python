"""Tests for wattnet.client.flatten.explode covering every payload shape."""

import pandas as pd

from wattnet.client import flatten


def test_explode_flat_records_pass_through(zones_payload):
    df = flatten.explode(zones_payload)

    assert list(df["zone"]) == ["ES"]
    assert list(df["neighbours"]) == [["FR", "PT"]]
    # Column order for a flat payload is whatever order the API's pydantic
    # model declares its fields in — preserved as-is, not reordered.
    assert list(df.columns) == [
        "zone",
        "full_name",
        "eic_code",
        "country_code",
        "country_name",
        "provider",
        "neighbours",
    ]


def test_explode_aggregate_records_pass_through(footprints_aggregate_payload):
    df = flatten.explode(footprints_aggregate_payload)

    assert len(df) == 1
    assert df.iloc[0]["value"] == 148.0
    assert "series" not in df.columns
    # Same rule: an aggregate record is already flat, so its column order is
    # exactly the API's declared field order (`value` lands wherever the
    # model puts it — here before `valid`/`zone_status`, not after).
    assert list(df.columns) == [
        "footprint_type",
        "scope",
        "zone",
        "unit",
        "coverage",
        "start",
        "end",
        "value",
        "valid",
        "zone_status",
        "aggregation_method",
    ]


def test_explode_series_without_block(footprints_payload):
    df = flatten.explode(footprints_payload)

    assert len(df) == 2
    assert list(df["value"]) == [150.0, 145.0]
    # Nesting order is a contract: record fields, then series fields, then
    # `timestamp`/`value`/`updated_at` from the exploded series — always in that order.
    assert list(df.columns) == [
        "footprint_type",
        "scope",
        "zone",
        "unit",
        "coverage",
        "valid",
        "zone_status",
        "timestamp",
        "value",
        "updated_at",
    ]


def test_explode_series_with_block(generation_payload):
    df = flatten.explode(generation_payload, block_key="production")

    assert len(df) == 4
    assert set(df["production_type"]) == {"solar", "wind_onshore"}
    solar_rows = df[df["production_type"] == "solar"]
    assert list(solar_rows["value"]) == [100.0, 110.0]
    # Same contract, one level deeper: record fields, then series fields,
    # then block fields, then `timestamp`/`value`/`updated_at` always last.
    assert list(df.columns) == [
        "zone",
        "unit",
        "valid",
        "zone_status",
        "production_type",
        "data_state",
        "datasource",
        "timestamp",
        "value",
        "updated_at",
    ]


def test_explode_empty_list_returns_empty_dataframe():
    df = flatten.explode([], block_key="production")

    assert df.empty


def test_explode_parses_timestamp_column_to_utc_datetime(footprints_payload):
    df = flatten.explode(footprints_payload)

    assert isinstance(df["timestamp"].dtype, pd.DatetimeTZDtype)
    assert str(df["timestamp"].dtype.tz) == "UTC"
    assert list(df["timestamp"]) == [
        pd.Timestamp("2026-01-01T00:00:00+00:00"),
        pd.Timestamp("2026-01-01T01:00:00+00:00"),
    ]


def test_explode_uses_the_points_of_a_series_and_adds_updated_at(
    footprints_payload,
):
    df = flatten.explode(footprints_payload)

    assert list(df.columns) == [
        "footprint_type",
        "scope",
        "zone",
        "unit",
        "coverage",
        "valid",
        "zone_status",
        "timestamp",
        "value",
        "updated_at",
    ]
    assert df.iloc[0]["value"] == 150.0
    assert str(df["updated_at"].dtype) == "datetime64[ns, UTC]"
    assert df.iloc[0]["updated_at"] == pd.Timestamp("2026-01-02T03:04:05", tz="UTC")


def test_explode_uses_the_points_of_a_block(generation_payload):
    df = flatten.explode(generation_payload, block_key="production")

    assert list(df.columns) == [
        "zone",
        "unit",
        "valid",
        "zone_status",
        "production_type",
        "data_state",
        "datasource",
        "timestamp",
        "value",
        "updated_at",
    ]
    assert list(df["value"]) == [100.0, 110.0, 200.0, 190.0]
    assert "points" not in df.columns


def test_explode_parses_the_updated_at_of_an_aggregate(footprints_aggregate_payload):
    footprints_aggregate_payload[0]["updated_at"] = "2026-01-02T03:04:05Z"

    df = flatten.explode(footprints_aggregate_payload)

    assert str(df["updated_at"].dtype) == "datetime64[ns, UTC]"


def test_explode_does_not_keep_the_values_list_as_a_column(
    generation_payload, footprints_payload
):
    pairs = [["2026-01-01T00:00:00+00:00", 1.0]]
    generation_payload[0]["series"][0]["production"][0]["values"] = pairs
    footprints_payload[0]["series"][0]["values"] = pairs

    generation = flatten.explode(generation_payload, block_key="production")
    footprints = flatten.explode(footprints_payload)

    assert "values" not in generation.columns
    assert "values" not in footprints.columns
