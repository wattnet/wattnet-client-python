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
    # The same contract as a series: the period, what it is, the value, then
    # the rest in the API's order.
    assert list(df.columns) == [
        "start",
        "end",
        "zone",
        "footprint_type",
        "scope",
        "value",
        "unit",
        "coverage",
        "valid",
        "zone_status",
        "aggregation_method",
    ]


def test_explode_series_without_block(footprints_payload):
    df = flatten.explode(footprints_payload)

    assert len(df) == 2
    assert list(df["value"]) == [150.0, 145.0]
    # The order is a contract: when, what the series is, the value, then the
    # quality and provenance of the data, and `updated_at` last.
    assert list(df.columns) == [
        "timestamp",
        "zone",
        "footprint_type",
        "scope",
        "value",
        "unit",
        "coverage",
        "valid",
        "zone_status",
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
        "timestamp",
        "zone",
        "production_type",
        "value",
        "unit",
        "valid",
        "zone_status",
        "data_state",
        "datasource",
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
        "timestamp",
        "zone",
        "footprint_type",
        "scope",
        "value",
        "unit",
        "coverage",
        "valid",
        "zone_status",
        "updated_at",
    ]
    assert df.iloc[0]["value"] == 150.0
    assert isinstance(df["updated_at"].dtype, pd.DatetimeTZDtype)
    assert str(df["updated_at"].dtype.tz) == "UTC"
    assert df.iloc[0]["updated_at"] == pd.Timestamp("2026-01-02T03:04:05", tz="UTC")


def test_explode_uses_the_points_of_a_block(generation_payload):
    df = flatten.explode(generation_payload, block_key="production")

    assert list(df.columns) == [
        "timestamp",
        "zone",
        "production_type",
        "value",
        "unit",
        "valid",
        "zone_status",
        "data_state",
        "datasource",
        "updated_at",
    ]
    assert list(df["value"]) == [100.0, 110.0, 200.0, 190.0]
    assert "points" not in df.columns


def test_explode_parses_the_updated_at_of_an_aggregate(footprints_aggregate_payload):
    footprints_aggregate_payload[0]["updated_at"] = "2026-01-02T03:04:05Z"

    df = flatten.explode(footprints_aggregate_payload)

    assert isinstance(df["updated_at"].dtype, pd.DatetimeTZDtype)
    assert str(df["updated_at"].dtype.tz) == "UTC"


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


def test_order_columns_keeps_source_as_provenance_without_a_zone():
    # In the factors `source` is where the factor comes from, not a zone.
    columns = ["factor_type", "production_type", "scope", "unit", "source", "year"]
    assert flatten.order_columns(columns + ["timestamp", "value", "updated_at"]) == [
        "timestamp",
        "production_type",
        "factor_type",
        "scope",
        "value",
        "unit",
        "source",
        "year",
        "updated_at",
    ]


def test_order_columns_puts_the_counterpart_zone_next_to_the_zone():
    columns = ["zone", "unit", "valid", "zone_status", "source", "timestamp", "value"]
    assert flatten.order_columns(columns) == [
        "timestamp",
        "zone",
        "source",
        "value",
        "unit",
        "valid",
        "zone_status",
    ]
