"""Generic flattening of wattnet-api's nested JSON payloads into DataFrames.

Every zone-scoped, non-aggregate endpoint follows the same shape: a record
per zone, holding a list of `series` (one version per `valid`/`zone_status`
combination), each optionally holding a list of `block`s grouped by some
category (production type, counterpart zone, ...), each holding a list of
`(timestamp, value)` tuples. Aggregate responses and flat listings (zones,
status) have no `series` and pass through as a single row per record.

Column order is a guaranteed contract, not incidental: it always follows the
nesting order of the source JSON (record fields, then series fields, then
block fields), with `timestamp`/`value` from an exploded series/block always
appended last. This falls out of two deterministic properties rather than
being hand-maintained per endpoint: wattnet-api's pydantic models serialize
their fields in declaration order, and Python dict merges (`{**a, **b}`)
preserve that order — so as long as each endpoint's field order doesn't
change API-side, the resulting DataFrame's column order won't change either.
The tests in `tests/unit/test_flatten.py` pin this down per payload shape.

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
    value_key: str = "values",
) -> pd.DataFrame:
    """Flatten a list of wattnet-api records into a DataFrame.

    :param records: JSON payload as returned by the API (a list of dicts).
    :param series_key: Key holding the nested list of series. Records
        lacking this key (aggregates, zones) are treated as already flat.
    :param block_key: Key holding a nested list of category blocks within
        each series, or None if series expose `value_key` directly.
    :param value_key: Key holding the list of `(timestamp, value)` tuples.
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
    return df


def _explode_series(
    base: Dict[str, Any],
    series_item: Dict[str, Any],
    block_key: Optional[str],
    value_key: str,
) -> List[Dict[str, Any]]:
    blocks = series_item.get(block_key) if block_key else None
    if blocks is None:
        series_base = {
            **base,
            **{k: v for k, v in series_item.items() if k != value_key},
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
            **{k: v for k, v in block.items() if k != value_key},
        }
        rows.extend(_explode_values(block_base, block[value_key]))
    return rows


def _explode_values(base: Dict[str, Any], values: List[Any]) -> List[Dict[str, Any]]:
    return [
        {**base, "timestamp": timestamp, "value": value} for timestamp, value in values
    ]
