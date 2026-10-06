"""Async raw HTTP client for the wattnet API — returns parsed JSON.

Async counterpart of `wattnet.client.WattnetRawClient`, built on `aiohttp`. It
exposes the same endpoints with the same arguments; every method is a
coroutine. Unlike the DataFrame client it does not import pandas, which makes
it a good fit for long-running services and frameworks such as Home Assistant.
"""

import asyncio
from datetime import datetime
from types import TracebackType
from typing import Any, Dict, List, Optional, Type, TypeVar

import aiohttp

from wattnet.client import decorators
from wattnet.client._util import parse_retry_after
from wattnet.client.async_auth import (
    TRANSIENT_ERRORS,
    AsyncCredentialsTokenProvider,
    AsyncStaticTokenProvider,
    AsyncTokenProvider,
    response_detail,
)
from wattnet.client.enums import (
    FactorType,
    FootprintType,
    ImpactType,
    ProductionType,
    Scope,
    Zone,
)
from wattnet.client.exceptions import ConfigurationError, WattnetAPIError
from wattnet.client.settings import (
    DEFAULT_BASE_URL,
    DEFAULT_RETRY_COUNT,
    DEFAULT_RETRY_DELAY,
    DEFAULT_STATIC_CACHE_TTL_SECONDS,
    DEFAULT_TIMEOUT,
    DEFAULT_TOKEN_URL,
    RETRYABLE_STATUS_CODES,
)

_Self = TypeVar("_Self", bound="AsyncWattnetRawClient")


class AsyncWattnetRawClient:
    """Async wrapper over the wattnet API's HTTP endpoints, returning raw JSON.

    Authenticate with either a pre-issued bearer token, or an email/password
    pair — in the latter case the client transparently fetches and caches a
    token from the wattnet token-request service, refreshing it as needed::

        async with AsyncWattnetRawClient(token="...") as client:
            zones = await client.get_zones()

    Pass your own `aiohttp.ClientSession` (e.g. Home Assistant's shared one) to
    reuse its connection pool; the client then never closes it. Without one,
    a session is created on first use and closed by `close()`.
    """

    def __init__(
        self,
        token: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        token_url: str = DEFAULT_TOKEN_URL,
        session: Optional[aiohttp.ClientSession] = None,
        timeout: float = DEFAULT_TIMEOUT,
        retry_count: int = DEFAULT_RETRY_COUNT,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ) -> None:
        """Configure auth and transport; see the class docstring for usage."""
        self._base_url = base_url.rstrip("/")
        self._session = session
        self._owns_session = session is None
        self._timeout = timeout
        self._retry_count = retry_count
        self._retry_delay = retry_delay
        self._auth: AsyncTokenProvider = _build_auth(
            token,
            email,
            password,
            token_url,
            session,
            timeout,
            retry_count,
            retry_delay,
        )

    def __repr__(self) -> str:
        """Show the base URL and auth mode — never any credentials."""
        auth_mode = type(self._auth).__name__
        return f"{type(self).__name__}(base_url={self._base_url!r}, auth={auth_mode})"

    def _get_session(self) -> aiohttp.ClientSession:
        """Return the HTTP session, creating it on first use if none was given."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._owns_session = True
            if isinstance(self._auth, AsyncCredentialsTokenProvider):
                self._auth.set_session(self._session)
        return self._session

    async def close(self) -> None:
        """Close the HTTP session, unless it was supplied by the caller."""
        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def __aenter__(self: _Self) -> _Self:
        """Support `async with AsyncWattnetRawClient(...) as client:` usage."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Close the HTTP session on exit (if owned)."""
        await self.close()

    # -- transport ---------------------------------------------------------

    async def _request(self, path: str, params: Dict[str, Any]) -> Any:
        """Perform a GET, retrying on transient errors, 401s, and 429/5xx.

        A 401 triggers one token refresh + retry (handled inline, not
        counted against `retry_count`). Connection/timeout errors and
        429/5xx responses are retried up to `retry_count` times, honoring
        the response's `Retry-After` header when present instead of the
        fixed `retry_delay`.
        """
        attempts = self._retry_count + 1
        for attempt in range(attempts):
            is_last_attempt = attempt == attempts - 1
            try:
                status, headers, body = await self._do_request(path, params)
                if status == 401:
                    self._auth.invalidate()
                    status, headers, body = await self._do_request(path, params)
            except TRANSIENT_ERRORS:
                if is_last_attempt:
                    raise
                await asyncio.sleep(self._retry_delay)
                continue
            if status in RETRYABLE_STATUS_CODES and not is_last_attempt:
                await asyncio.sleep(
                    parse_retry_after(headers.get("Retry-After"), self._retry_delay)
                )
                continue
            return _parse_response(status, body)
        raise AssertionError(
            "unreachable: loop always returns or raises"
        )  # pragma: no cover

    async def _do_request(
        self, path: str, params: Dict[str, Any]
    ) -> "tuple[int, Any, Any]":
        session = self._get_session()  # before the token: the provider shares it
        token = await self._auth.get_token()
        async with session.get(
            f"{self._base_url}{path}",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=aiohttp.ClientTimeout(total=self._timeout),
        ) as response:
            if response.status < 400:
                return (
                    response.status,
                    response.headers,
                    await response.json(content_type=None),
                )
            return response.status, response.headers, await response_detail(response)

    # -- zones ---------------------------------------------------------------

    @decorators.acached(ttl=DEFAULT_STATIC_CACHE_TTL_SECONDS)
    @decorators.get("/zones")
    async def get_zones(self) -> List[Dict[str, Any]]:
        """List all configured zones with their metadata and neighbours."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    # -- energy metrics --------------------------------------------------

    @decorators.get("/generation")
    async def get_generation(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        production_type: Optional[ProductionType] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Electricity generation by production type for a zone or coordinate."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/load")
    async def get_load(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Total electricity demand for a zone or coordinate."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/imports")
    async def get_imports(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        source_zone: Optional[Zone] = None,
        source_lat: Optional[float] = None,
        source_lon: Optional[float] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Electricity imports into a zone, optionally filtered by origin zone."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/exports")
    async def get_exports(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        destination_zone: Optional[Zone] = None,
        destination_lat: Optional[float] = None,
        destination_lon: Optional[float] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Electricity exports from a zone, optionally filtered by destination."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/mix")
    async def get_mix(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        production_type: Optional[ProductionType] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Return the flow-traced generation mix by production type for a zone."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    # -- environmental metrics -----------------------------------------

    @decorators.get("/footprints")
    async def get_footprints(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        footprint_type: Optional[FootprintType] = None,
        scope: Optional[Scope] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        aggregate: bool = False,
        use_global: bool = True,
    ) -> List[Dict[str, Any]]:
        """Carbon/water footprint of electricity consumption in a zone.

        Set `aggregate=True` (with `start`/`end` required) for a single
        aggregated value per zone/series instead of a time series.
        """
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/impacts")
    async def get_impacts(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        impact_type: Optional[ImpactType] = None,
        scope: Optional[Scope] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        aggregate: bool = False,
        use_global: bool = True,
    ) -> List[Dict[str, Any]]:
        """Water impact of electricity consumption in a zone."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/environmental-score")
    async def get_environmental_score(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        scope: Optional[Scope] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        aggregate: bool = False,
        use_global: bool = True,
    ) -> List[Dict[str, Any]]:
        """Return the EnvironmentalScore (0-100) of electricity use in a zone."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    # -- shares metrics --------------------------------------------------

    @decorators.get("/flow-share")
    async def get_flow_share(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        destination_zone: Optional[Zone] = None,
        destination_lat: Optional[float] = None,
        destination_lon: Optional[float] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Share of an origin zone's production exported to each destination."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/mix-share")
    async def get_mix_share(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        origin_zone: Optional[Zone] = None,
        origin_lat: Optional[float] = None,
        origin_lon: Optional[float] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Share of a destination zone's mix coming from each origin zone."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/footprint-share")
    async def get_footprint_share(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        source_zone: Optional[Zone] = None,
        source_lat: Optional[float] = None,
        source_lon: Optional[float] = None,
        footprint_type: Optional[FootprintType] = None,
        scope: Optional[Scope] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Footprint of a destination zone decomposed by origin zone."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/impact-share")
    async def get_impact_share(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        source_zone: Optional[Zone] = None,
        source_lat: Optional[float] = None,
        source_lon: Optional[float] = None,
        impact_type: Optional[ImpactType] = None,
        scope: Optional[Scope] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Impact of a destination zone decomposed by origin zone."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    # -- factors -----------------------------------------------------------

    @decorators.acached(ttl=DEFAULT_STATIC_CACHE_TTL_SECONDS)
    @decorators.get("/factors")
    async def get_factors(
        self,
        factor_type: Optional[FactorType] = None,
        scope: Optional[Scope] = None,
        production_type: Optional[ProductionType] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        aggregate: bool = False,
    ) -> List[Dict[str, Any]]:
        """Emission/consumption factors used in wattnet's calculations.

        Zone-independent: these are global factors, not per-zone metrics.
        """
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    # -- status --------------------------------------------------------------

    @decorators.get("/status")
    async def get_status(self) -> Dict[str, str]:
        """Health of the API and all its upstream dependencies."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/status/storage")
    async def get_status_storage(self) -> Dict[str, str]:
        """Health of the wattnet-storage backend."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/status/entso-e")
    async def get_status_entsoe(self) -> Dict[str, str]:
        """Health of the ENTSO-E upstream data provider."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/status/elexon")
    async def get_status_elexon(self) -> Dict[str, str]:
        """Health of the Elexon upstream data provider."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/status/epias")
    async def get_status_epias(self) -> Dict[str, str]:
        """Health of the EPIAS upstream data provider."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get


def _build_auth(
    token: Optional[str],
    email: Optional[str],
    password: Optional[str],
    token_url: str,
    session: Optional[aiohttp.ClientSession],
    timeout: float,
    retry_count: int,
    retry_delay: float,
) -> AsyncTokenProvider:
    if token is not None and (email is not None or password is not None):
        raise ConfigurationError(
            "Provide either `token` or `email`+`password`, not both."
        )
    if token is not None:
        return AsyncStaticTokenProvider(token)
    if email is not None and password is not None:
        return AsyncCredentialsTokenProvider(
            email,
            password,
            token_url,
            session,  # type: ignore[arg-type]  # set lazily by the client
            timeout,
            retry_count,
            retry_delay,
        )
    raise ConfigurationError(
        "Must provide either `token`, or both `email` and `password`."
    )


def _parse_response(status: int, body: Any) -> Any:
    if status < 400:
        return body
    raise WattnetAPIError(
        f"wattnet API request failed ({status}): {body}",
        status_code=status,
        detail=body,
    )
