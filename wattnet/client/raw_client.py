"""Raw HTTP client for the wattnet API — returns parsed JSON (dicts/lists).

For a friendlier client that returns pandas DataFrames, use
`wattnet.client.WattnetClient` instead; it subclasses this one and is what
most callers should reach for.
"""

import time
from datetime import datetime
from types import TracebackType
from typing import Any, Dict, List, Optional, Type, TypeVar

import requests

from wattnet.client import decorators
from wattnet.client._util import error_code, error_detail, parse_retry_after
from wattnet.client.auth import (
    ClientCredentialsTokenProvider,
    StaticTokenProvider,
    TokenProvider,
)
from wattnet.client.enums import (
    FactorType,
    FootprintType,
    ImpactType,
    ProductionType,
    Resolution,
    Scope,
    Zone,
)
from wattnet.client.exceptions import ConfigurationError, WattnetAPIError
from wattnet.client.settings import (
    DEFAULT_BASE_URL,
    DEFAULT_ISSUER_URL,
    DEFAULT_RETRY_COUNT,
    DEFAULT_RETRY_DELAY,
    DEFAULT_STATIC_CACHE_TTL_SECONDS,
    DEFAULT_TIMEOUT,
    DEFAULT_TOKEN_URL,
    RETRYABLE_STATUS_CODES,
)

_Self = TypeVar("_Self", bound="WattnetRawClient")


class WattnetRawClient:
    """Thin wrapper over the wattnet API's HTTP endpoints, returning raw JSON.

    Authenticate with either a pre-issued bearer token, or the `client_id` and
    `client_secret` of a wattnet credential — in the latter case the client
    transparently fetches and caches a token (OAuth 2.0 `client_credentials`),
    refreshing it as needed::

        WattnetRawClient(token="...")
        WattnetRawClient(client_id="...", client_secret="...")
    """

    def __init__(
        self,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        issuer_url: str = DEFAULT_ISSUER_URL,
        token_url: Optional[str] = DEFAULT_TOKEN_URL,
        session: Optional[requests.Session] = None,
        timeout: float = DEFAULT_TIMEOUT,
        retry_count: int = DEFAULT_RETRY_COUNT,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        compress: bool = True,
    ) -> None:
        """Configure auth and transport; see the class docstring for usage.

        :param compress: Ask the API for compressed answers (gzip, and br or zstd
            when their packages are installed), which are several times smaller
            and are decompressed transparently. `False` asks for none.
        """
        self._base_url = base_url.rstrip("/")
        self._session = session or requests.Session()
        self._timeout = timeout
        self._retry_count = retry_count
        self._retry_delay = retry_delay
        self._compress = compress
        self._auth: TokenProvider = _build_auth(
            token,
            client_id,
            client_secret,
            issuer_url,
            token_url,
            self._session,
            timeout,
            retry_count,
            retry_delay,
        )

    def __repr__(self) -> str:
        """Show the base URL and auth mode — never any credentials."""
        auth_mode = type(self._auth).__name__
        return f"{type(self).__name__}(base_url={self._base_url!r}, auth={auth_mode})"

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self: _Self) -> _Self:
        """Support `with WattnetClient(...) as client:` usage."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Close the underlying HTTP session on exit."""
        self.close()

    # -- transport ---------------------------------------------------------

    def _request(self, path: str, params: Dict[str, Any]) -> Any:
        """Perform a GET, retrying on transient errors, 401s, and 429/5xx.

        A 401 triggers one token refresh + retry (handled inline, not
        counted against `retry_count`). Connection/timeout errors and
        429/5xx responses are retried up to `retry_count` times, honoring
        the response's `Retry-After` header when present (on 429s) instead
        of the fixed `retry_delay`.
        """
        attempts = self._retry_count + 1
        for attempt in range(attempts):
            is_last_attempt = attempt == attempts - 1
            try:
                response = self._do_request(path, params)
                if response.status_code == 401:
                    self._auth.invalidate()
                    response = self._do_request(path, params)
            except decorators._TRANSIENT_ERRORS:
                if is_last_attempt:
                    raise
                time.sleep(self._retry_delay)
                continue
            if response.status_code in RETRYABLE_STATUS_CODES and not is_last_attempt:
                time.sleep(_retry_delay_for(response, self._retry_delay))
                continue
            return _parse_response(response)
        raise AssertionError(
            "unreachable: loop always returns or raises"
        )  # pragma: no cover

    def _do_request(self, path: str, params: Dict[str, Any]) -> requests.Response:
        return self._session.get(
            f"{self._base_url}{path}",
            params=params,
            headers=_headers(self._auth.get_token(), self._compress),
            timeout=self._timeout,
        )

    # -- zones ---------------------------------------------------------------

    @decorators.cached(ttl=DEFAULT_STATIC_CACHE_TTL_SECONDS)
    @decorators.get("/zones")
    def get_zones(self) -> List[Dict[str, Any]]:
        """List all configured zones with their metadata and neighbours."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    # -- energy metrics --------------------------------------------------

    @decorators.get("/generation")
    def get_generation(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        production_type: Optional[ProductionType] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        resolution: Optional[Resolution] = None,
    ) -> List[Dict[str, Any]]:
        """Electricity generation by production type for a zone or coordinate."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/load")
    def get_load(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        resolution: Optional[Resolution] = None,
    ) -> List[Dict[str, Any]]:
        """Total electricity demand for a zone or coordinate."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/imports")
    def get_imports(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        source_zone: Optional[Zone] = None,
        source_lat: Optional[float] = None,
        source_lon: Optional[float] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        resolution: Optional[Resolution] = None,
    ) -> List[Dict[str, Any]]:
        """Electricity imports into a zone, optionally filtered by origin zone."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/exports")
    def get_exports(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        destination_zone: Optional[Zone] = None,
        destination_lat: Optional[float] = None,
        destination_lon: Optional[float] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        resolution: Optional[Resolution] = None,
    ) -> List[Dict[str, Any]]:
        """Electricity exports from a zone, optionally filtered by destination."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/mix")
    def get_mix(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        production_type: Optional[ProductionType] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        resolution: Optional[Resolution] = None,
    ) -> List[Dict[str, Any]]:
        """Return the flow-traced generation mix by production type for a zone."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    # -- environmental metrics -----------------------------------------

    @decorators.get("/footprints")
    def get_footprints(
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
        resolution: Optional[Resolution] = None,
    ) -> List[Dict[str, Any]]:
        """Carbon/water footprint of electricity consumption in a zone.

        Set `aggregate=True` (with `start`/`end` required) for a single
        aggregated value per zone/series instead of a time series.
        """
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/impacts")
    def get_impacts(
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
        resolution: Optional[Resolution] = None,
    ) -> List[Dict[str, Any]]:
        """Water impact of electricity consumption in a zone."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/environmental-score")
    def get_environmental_score(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        scope: Optional[Scope] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        aggregate: bool = False,
        use_global: bool = True,
        resolution: Optional[Resolution] = None,
    ) -> List[Dict[str, Any]]:
        """Return the EnvironmentalScore (0-100) of electricity use in a zone."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    # -- shares metrics --------------------------------------------------

    @decorators.get("/flow-share")
    def get_flow_share(
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
    def get_mix_share(
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
    def get_footprint_share(
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
    def get_impact_share(
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

    @decorators.cached(ttl=DEFAULT_STATIC_CACHE_TTL_SECONDS)
    @decorators.get("/factors")
    def get_factors(
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
    def get_status(self) -> Dict[str, str]:
        """Health of the API and all its upstream dependencies."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/status/storage")
    def get_status_storage(self) -> Dict[str, str]:
        """Health of the wattnet-storage backend."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/status/entso-e")
    def get_status_entsoe(self) -> Dict[str, str]:
        """Health of the ENTSO-E upstream data provider."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/status/elexon")
    def get_status_elexon(self) -> Dict[str, str]:
        """Health of the Elexon upstream data provider."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get

    @decorators.get("/status/epias")
    def get_status_epias(self) -> Dict[str, str]:
        """Health of the EPIAS upstream data provider."""
        raise NotImplementedError  # pragma: no cover - replaced by @decorators.get


def _build_auth(
    token: Optional[str],
    client_id: Optional[str],
    client_secret: Optional[str],
    issuer_url: str,
    token_url: Optional[str],
    session: requests.Session,
    timeout: float,
    retry_count: int,
    retry_delay: float,
) -> TokenProvider:
    if token is not None and (client_id is not None or client_secret is not None):
        raise ConfigurationError(
            "Provide either `token` or `client_id`+`client_secret`, not both."
        )
    if token is not None:
        return StaticTokenProvider(token)
    if client_id is not None and client_secret is not None:
        return ClientCredentialsTokenProvider(
            client_id,
            client_secret,
            issuer_url,
            token_url,
            session,
            timeout,
            retry_count,
            retry_delay,
        )
    raise ConfigurationError(
        "Must provide either `token`, or both `client_id` and `client_secret`."
    )


def _headers(token: str, compress: bool) -> Dict[str, str]:
    """Headers of a request; without compression the answer is asked as it is."""
    headers = {"Authorization": f"Bearer {token}"}
    if not compress:
        headers["Accept-Encoding"] = "identity"
    return headers


def _retry_delay_for(response: requests.Response, default: float) -> float:
    """Seconds to wait before retrying, honoring a numeric `Retry-After`."""
    return parse_retry_after(response.headers.get("Retry-After"), default)


def _parse_response(response: requests.Response) -> Any:
    if response.ok:
        return response.json()
    detail = error_detail(response)
    raise WattnetAPIError(
        f"wattnet API request failed ({response.status_code}): {detail}",
        status_code=response.status_code,
        detail=detail,
        code=error_code(response),
    )
