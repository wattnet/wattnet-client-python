"""Decorators that turn typed method stubs into a full HTTP + pandas client.

- `@get(path)` — declares a raw endpoint. The decorated method's body is
  never executed; only its signature is inspected, so each endpoint of
  `WattnetRawClient` is just a type-hinted stub plus a docstring.
- `@retry(...)` — retries a method on transient network errors.
- `@cached(ttl=...)` — caches a method's return value per-instance, keyed by
  its arguments, for near-static endpoints (zones, factors).
- `@acached(ttl=...)` — same as `@cached`, for coroutine methods.
- `@dataframe(...)` — flattens the JSON returned by a `WattnetClient`
  override (which simply delegates to the raw method) into a DataFrame.
- `@adataframe(...)` — same as `@dataframe`, for coroutine methods.

pandas is only imported when a `@dataframe` method actually runs, so the raw
and async clients work without paying for it at import time.
"""

import functools
import inspect
import time
from datetime import datetime, timezone
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Optional,
    Tuple,
    Type,
    TypeVar,
)

import requests

if TYPE_CHECKING:  # pragma: no cover
    import pandas as pd

F = TypeVar("F", bound=Callable[..., Any])


def get(path: str) -> Callable[[F], F]:
    """Turn a typed method stub into a live GET call to `path`.

    At call time, bound arguments (aside from `self`) become query params:
    `None` values are dropped, `datetime`s are serialized to ISO 8601
    (assuming UTC if naive), and `bool`s to lowercase `"true"`/`"false"`.
    """

    def decorator(func: F) -> F:
        signature = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            bound = signature.bind(self, *args, **kwargs)
            bound.apply_defaults()
            params = {
                name: _serialize_param(value)
                for name, value in bound.arguments.items()
                if name != "self" and value is not None
            }
            return self._request(path, params)

        return wrapper  # type: ignore[return-value]

    return decorator


def _serialize_param(value: Any) -> Any:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    return value


_TRANSIENT_ERRORS: Tuple[Type[BaseException], ...] = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
)


def retry(
    exceptions: Tuple[Type[BaseException], ...] = _TRANSIENT_ERRORS,
    count: Optional[int] = None,
    delay: Optional[float] = None,
) -> Callable[[F], F]:
    """Retry a function or method on transient network errors.

    Usable two ways:

    - `@retry(count=3, delay=1.0)` — fixed settings, works on any callable,
      bound method or plain function alike.
    - `@retry()` on an instance method — reads `_retry_count`/`_retry_delay`
      off the instance (`self`, i.e. the wrapped call's first argument) on
      every call, so it follows whatever the client was constructed with.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempts_left = count if count is not None else args[0]._retry_count
            wait = delay if delay is not None else args[0]._retry_delay
            attempts = attempts_left + 1
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == attempts - 1:
                        raise
                    time.sleep(wait)

        return wrapper  # type: ignore[return-value]

    return decorator


def cached(ttl: float) -> Callable[[F], F]:
    """Cache a method's result per-instance, keyed by its bound arguments.

    Stores entries on the instance itself (`self._response_cache`), not in a
    module-level dict, so cached data is garbage-collected along with the
    client that fetched it rather than leaking across instances. Meant for
    endpoints that barely change (zones, factors) so repeated calls within a
    notebook session don't each cost a round trip.
    """

    def decorator(func: F) -> F:
        signature = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            bound = signature.bind(self, *args, **kwargs)
            bound.apply_defaults()
            key = tuple(
                sorted(
                    (name, value)
                    for name, value in bound.arguments.items()
                    if name != "self"
                )
            )
            store: Dict[Any, Tuple[float, Any]] = self.__dict__.setdefault(
                "_response_cache", {}
            )
            cache_key = (func.__name__, key)
            now = time.monotonic()
            entry = store.get(cache_key)
            if entry is not None and now - entry[0] < ttl:
                return entry[1]
            value = func(self, *args, **kwargs)
            store[cache_key] = (now, value)
            return value

        return wrapper  # type: ignore[return-value]

    return decorator


def acached(ttl: float) -> Callable[[F], F]:
    """Async counterpart of `cached`, for coroutine methods.

    Same per-instance store and `(name, arguments)` keys as `cached`. Only
    successful results are stored, so a failed call is retried next time.
    """

    def decorator(func: F) -> F:
        signature = inspect.signature(func)

        @functools.wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            bound = signature.bind(self, *args, **kwargs)
            bound.apply_defaults()
            key = tuple(
                sorted(
                    (name, value)
                    for name, value in bound.arguments.items()
                    if name != "self"
                )
            )
            store: Dict[Any, Tuple[float, Any]] = self.__dict__.setdefault(
                "_response_cache", {}
            )
            cache_key = (func.__name__, key)
            now = time.monotonic()
            entry = store.get(cache_key)
            if entry is not None and now - entry[0] < ttl:
                return entry[1]
            value = await func(self, *args, **kwargs)
            store[cache_key] = (now, value)
            return value

        return wrapper  # type: ignore[return-value]

    return decorator


def _frame(
    result: Any,
    series: Optional[str],
    block: Optional[str],
    value_key: str,
    record: bool,
) -> "pd.DataFrame":
    import pandas as pd

    from wattnet.client import flatten

    if record:
        return pd.DataFrame([result])
    return flatten.explode(
        result, series_key=series, block_key=block, value_key=value_key
    )


def dataframe(
    series: Optional[str] = "series",
    block: Optional[str] = None,
    value_key: str = "values",
    record: bool = False,
) -> Callable[[F], F]:
    """Flatten the JSON returned by the wrapped method into a DataFrame.

    The wrapped method's body should simply delegate to the raw client
    method of the same name (typically `return super().method_name(...)`);
    this decorator turns its JSON result into a DataFrame.

    :param series: Key holding the list of per-status series, or None if the
        payload is already a flat list of records (e.g. zones, aggregates).
    :param block: Key holding a nested list of category blocks within each
        series, or None if series entries expose `values` directly.
    :param record: Set for endpoints returning a single JSON object (e.g.
        status checks) rather than a list — wraps it as a one-row DataFrame.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> "pd.DataFrame":
            result = func(self, *args, **kwargs)
            return _frame(result, series, block, value_key, record)

        return wrapper  # type: ignore[return-value]

    return decorator


def adataframe(
    series: Optional[str] = "series",
    block: Optional[str] = None,
    value_key: str = "values",
    record: bool = False,
) -> Callable[[F], F]:
    """Async counterpart of `dataframe`, for coroutine methods.

    Takes the same parameters; the wrapped coroutine is awaited and its JSON
    result flattened into a DataFrame.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> "pd.DataFrame":
            result = await func(self, *args, **kwargs)
            return _frame(result, series, block, value_key, record)

        return wrapper  # type: ignore[return-value]

    return decorator
