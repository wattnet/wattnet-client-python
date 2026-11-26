"""Generic flattening of wattnet-api's nested JSON payloads into DataFrames.

Every zone-scoped, non-aggregate endpoint follows the same shape: a record
per zone, holding a list of `series` (one version per `valid`/`zone_status`
combination), each optionally holding a list of `block`s grouped by some
category (production type, counterpart zone, ...), each holding a list of
points. Aggregate responses and flat listings (zones,
status) have no `series` and pass through as a single row per record.

Column order is a guaranteed contract, the same for every endpoint: first when
(`timestamp`, or `start` and `end` for an aggregate), then what the series is
(`zone`, the counterpart zone, the type and the `scope`), then `value` and
`unit`, then the quality and the provenance of the data (`valid`,
`zone_status`, `data_state`, `datasource`, `coverage`...) in the order the API
sends them, and `updated_at` last. `source` is the counterpart zone only next to
a `zone`; in the factors it is where the factor comes from and stays with the
provenance. The tests in `tests/unit/test_flatten.py` pin this down per payload
shape.

Every series or block holds its data as `points`, objects with `timestamp`,
`value` and `updated_at` (the moment that version of the value was stored). The
API's older `values` (`[timestamp, value]` pairs) is not read: the client needs
an API that sends `points`.

A resulting `timestamp` column is always parsed to a tz-aware (UTC)
`datetime64` dtype rather than left as the API's raw ISO 8601
string, so callers get a plottable/resamplable column for free.
"""

from typing import Any, Dict, List, Optional

import pandas as pd


def explode(
    records: List[Dict[str, Any]],
    series_key: Optional[str] = "series",
    block_key: Optional[str] = None,
    value_key: str = "points",
) -> pd.DataFrame:
    """Flatten a list of wattnet-api records into a DataFrame.

    :param records: JSON payload as returned by the API (a list of dicts).
    :param series_key: Key holding the nested list of series. Records
        lacking this key (aggregates, zones) are treated as already flat.
    :param block_key: Key holding a nested list of category blocks within
        each series, or None if series expose `value_key` directly.
    :param value_key: Key holding the list of points (objects with `timestamp`,
        `value` and `updated_at`).
    """
    rows: List[Dict[str, Any]] = []
    for record in records:
        series_list = record.get(series_key) if series_key else None
        if series_list is None:
            rows.append(record)
            continue
        base = {k: v for k, v in record.items() if k != series_key}
        for series_item in series_list:
            rows.extend(_explode_series(base, series_item, block_key, value_key))
    df = pd.DataFrame(rows)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    if "updated_at" in df.columns:
        df["updated_at"] = pd.to_datetime(df["updated_at"], utc=True)
    return df[order_columns(list(df.columns))]


_WHEN = ("timestamp", "start", "end")
_SERIES = (
    "zone",
    "source",
    "destination",
    "origin",
    "production_type",
    "footprint_type",
    "impact_type",
    "factor_type",
    "scope",
)
_VALUE = ("value", "unit")
_LAST = ("updated_at",)


def order_columns(columns: List[str]) -> List[str]:
    """Return *columns* in the order of the contract (see the module docstring)."""
    series = [
        c for c in _SERIES if c in columns and (c != "source" or "zone" in columns)
    ]
    lead = [c for c in _WHEN if c in columns] + series
    lead += [c for c in _VALUE if c in columns]
    tail = [c for c in _LAST if c in columns]
    return lead + [c for c in columns if c not in lead and c not in tail] + tail


def _explode_series(
    base: Dict[str, Any],
    series_item: Dict[str, Any],
    block_key: Optional[str],
    value_key: str,
) -> List[Dict[str, Any]]:
    leaf_keys = {value_key, "values"}
    blocks = series_item.get(block_key) if block_key else None
    if blocks is None:
        series_base = {
            **base,
            **{k: v for k, v in series_item.items() if k not in leaf_keys},
        }
        return _explode_values(series_base, series_item[value_key])

    series_base = {
        **base,
        **{k: v for k, v in series_item.items() if k != block_key},
    }
    rows: List[Dict[str, Any]] = []
    for block in blocks:
        block_base = {
            **series_base,
            **{k: v for k, v in block.items() if k not in leaf_keys},
        }
        rows.extend(_explode_values(block_base, block[value_key]))
    return rows


def _explode_values(
    base: Dict[str, Any], points: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    return [{**base, **point} for point in points]
