"""Tests for the @get, @retry, and @dataframe decorators."""

from datetime import datetime, timezone

import pandas as pd
import pytest
import requests

from wattnet.client.decorators import cached, dataframe, get, retry


class _FakeRawEndpoint:
    """Stand-in for WattnetRawClient: records the params passed to `_request`."""

    def __init__(self):
        self.last_path = None
        self.last_params = None

    def _request(self, path, params):
        self.last_path = path
        self.last_params = params
        return {"ok": True}

    @get("/widgets")
    def get_widgets(
        self,
        name=None,
        count=None,
        start=None,
        aggregate=False,
    ): ...


def test_get_decorator_drops_none_params():
    endpoint = _FakeRawEndpoint()
    endpoint.get_widgets(name="foo")

    assert endpoint.last_path == "/widgets"
    assert endpoint.last_params == {"name": "foo", "aggregate": "false"}


def test_get_decorator_serializes_datetime_to_isoformat():
    endpoint = _FakeRawEndpoint()
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    endpoint.get_widgets(start=start)

    assert endpoint.last_params["start"] == "2026-01-01T00:00:00+00:00"


def test_get_decorator_assumes_utc_for_naive_datetime():
    endpoint = _FakeRawEndpoint()
    endpoint.get_widgets(start=datetime(2026, 1, 1))

    assert endpoint.last_params["start"] == "2026-01-01T00:00:00+00:00"


def test_get_decorator_serializes_bool_lowercase():
    endpoint = _FakeRawEndpoint()
    endpoint.get_widgets(aggregate=True)

    assert endpoint.last_params["aggregate"] == "true"


class _FlakyTransport:
    def __init__(self, fail_times):
        self._retry_count = 3
        self._retry_delay = 0
        self._fail_times = fail_times
        self.calls = 0

    @retry()
    def call(self):
        self.calls += 1
        if self.calls <= self._fail_times:
            raise requests.exceptions.ConnectionError("boom")
        return "success"


def test_retry_succeeds_after_transient_failures():
    transport = _FlakyTransport(fail_times=2)

    assert transport.call() == "success"
    assert transport.calls == 3


def test_retry_raises_after_exhausting_attempts():
    transport = _FlakyTransport(fail_times=10)

    with pytest.raises(requests.exceptions.ConnectionError):
        transport.call()
    assert transport.calls == 4  # 1 initial attempt + 3 retries


def test_retry_with_explicit_count_works_on_plain_functions():
    calls = {"count": 0}

    @retry(count=2, delay=0)
    def flaky():
        calls["count"] += 1
        if calls["count"] <= 1:
            raise requests.exceptions.ConnectionError("boom")
        return "success"

    assert flaky() == "success"
    assert calls["count"] == 2


class _CountingEndpoint:
    def __init__(self):
        self.calls = 0

    @cached(ttl=60)
    def get_thing(self, x=None):
        self.calls += 1
        return {"x": x, "call": self.calls}


def test_cached_returns_same_value_without_recalling():
    endpoint = _CountingEndpoint()

    first = endpoint.get_thing(x=1)
    second = endpoint.get_thing(x=1)

    assert first == second
    assert endpoint.calls == 1


def test_cached_distinguishes_by_arguments():
    endpoint = _CountingEndpoint()

    endpoint.get_thing(x=1)
    endpoint.get_thing(x=2)

    assert endpoint.calls == 2


def test_cached_is_isolated_per_instance():
    a = _CountingEndpoint()
    b = _CountingEndpoint()

    a.get_thing(x=1)
    b.get_thing(x=1)

    assert a.calls == 1
    assert b.calls == 1


def test_cached_expires_after_ttl(monkeypatch):
    endpoint = _CountingEndpoint()
    now = [1000.0]
    monkeypatch.setattr("wattnet.client.decorators.time.monotonic", lambda: now[0])

    endpoint.get_thing(x=1)
    now[0] += 61
    endpoint.get_thing(x=1)

    assert endpoint.calls == 2


class _FakePandasEndpoint:
    @dataframe(block="items")
    def get_nested(self):
        return [
            {
                "zone": "ES",
                "series": [
                    {
                        "valid": True,
                        "items": [
                            {
                                "kind": "a",
                                "points": [
                                    {
                                        "timestamp": "2026-01-01T00:00:00Z",
                                        "value": 1,
                                        "updated_at": "2026-01-02T03:04:05+00:00",
                                    },
                                    {
                                        "timestamp": "2026-01-01T01:00:00Z",
                                        "value": 2,
                                        "updated_at": "2026-01-02T03:04:05+00:00",
                                    },
                                ],
                            }
                        ],
                    }
                ],
            }
        ]

    @dataframe(record=True)
    def get_status(self):
        return {"storage": "up"}


def test_dataframe_decorator_explodes_nested_json():
    df = _FakePandasEndpoint().get_nested()

    assert isinstance(df, pd.DataFrame)
    assert list(df["value"]) == [1, 2]


def test_dataframe_decorator_wraps_single_record():
    df = _FakePandasEndpoint().get_status()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]["storage"] == "up"
