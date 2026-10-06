"""Async DataFrame-returning client for the wattnet API.

Async counterpart of `wattnet.client.WattnetClient`: every method mirrors
`AsyncWattnetRawClient`'s method of the same name, but is a coroutine that
returns a `pandas.DataFrame` instead of raw JSON. Use
`AsyncWattnetRawClient` directly if you need the untouched JSON payload or
do not want pandas.
"""

from datetime import datetime
from typing import Optional

import pandas as pd

from wattnet.client.async_raw_client import AsyncWattnetRawClient
from wattnet.client.decorators import adataframe
from wattnet.client.enums import (
    FactorType,
    FootprintType,
    ImpactType,
    ProductionType,
    Scope,
    Zone,
)


class AsyncWattnetClient(AsyncWattnetRawClient):
    """Query the wattnet API asynchronously and get pandas DataFrames back.

    async with AsyncWattnetClient(token="...") as client:
        df = await client.get_generation(zone="ES", start=..., end=...)
    """

    # -- zones -----------------------------------------------------------

    @adataframe()
    async def get_zones(self) -> pd.DataFrame:
        """List all configured zones with their metadata and neighbours."""
        return await super().get_zones()

    # -- energy metrics --------------------------------------------------

    @adataframe(block="production")
    async def get_generation(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        production_type: Optional[ProductionType] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Electricity generation by production type for a zone or coordinate."""
        return await super().get_generation(
            zone=zone,
            lat=lat,
            lon=lon,
            production_type=production_type,
            start=start,
            end=end,
        )

    @adataframe(block="blocks")
    async def get_load(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Total electricity demand for a zone or coordinate."""
        return await super().get_load(zone=zone, lat=lat, lon=lon, start=start, end=end)

    @adataframe(block="imports")
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
    ) -> pd.DataFrame:
        """Electricity imports into a zone, optionally filtered by origin zone."""
        return await super().get_imports(
            zone=zone,
            lat=lat,
            lon=lon,
            source_zone=source_zone,
            source_lat=source_lat,
            source_lon=source_lon,
            start=start,
            end=end,
        )

    @adataframe(block="exports")
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
    ) -> pd.DataFrame:
        """Electricity exports from a zone, optionally filtered by destination."""
        return await super().get_exports(
            zone=zone,
            lat=lat,
            lon=lon,
            destination_zone=destination_zone,
            destination_lat=destination_lat,
            destination_lon=destination_lon,
            start=start,
            end=end,
        )

    @adataframe(block="production")
    async def get_mix(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        production_type: Optional[ProductionType] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Return the flow-traced generation mix by production type for a zone."""
        return await super().get_mix(
            zone=zone,
            lat=lat,
            lon=lon,
            production_type=production_type,
            start=start,
            end=end,
        )

    # -- environmental metrics -----------------------------------------

    @adataframe()
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
    ) -> pd.DataFrame:
        """Carbon/water footprint of electricity consumption in a zone.

        Set `aggregate=True` (with `start`/`end` required) for a single
        aggregated value per zone/series instead of a time series.
        """
        return await super().get_footprints(
            zone=zone,
            lat=lat,
            lon=lon,
            footprint_type=footprint_type,
            scope=scope,
            start=start,
            end=end,
            aggregate=aggregate,
            use_global=use_global,
        )

    @adataframe()
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
    ) -> pd.DataFrame:
        """Water impact of electricity consumption in a zone."""
        return await super().get_impacts(
            zone=zone,
            lat=lat,
            lon=lon,
            impact_type=impact_type,
            scope=scope,
            start=start,
            end=end,
            aggregate=aggregate,
            use_global=use_global,
        )

    @adataframe()
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
    ) -> pd.DataFrame:
        """Return the EnvironmentalScore (0-100) of electricity use in a zone."""
        return await super().get_environmental_score(
            zone=zone,
            lat=lat,
            lon=lon,
            scope=scope,
            start=start,
            end=end,
            aggregate=aggregate,
            use_global=use_global,
        )

    # -- shares metrics --------------------------------------------------

    @adataframe(block="flows")
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
    ) -> pd.DataFrame:
        """Share of an origin zone's production exported to each destination."""
        return await super().get_flow_share(
            zone=zone,
            lat=lat,
            lon=lon,
            destination_zone=destination_zone,
            destination_lat=destination_lat,
            destination_lon=destination_lon,
            start=start,
            end=end,
        )

    @adataframe(block="shares")
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
    ) -> pd.DataFrame:
        """Share of a destination zone's mix coming from each origin zone."""
        return await super().get_mix_share(
            zone=zone,
            lat=lat,
            lon=lon,
            origin_zone=origin_zone,
            origin_lat=origin_lat,
            origin_lon=origin_lon,
            start=start,
            end=end,
        )

    @adataframe(block="blocks")
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
    ) -> pd.DataFrame:
        """Footprint of a destination zone decomposed by origin zone."""
        return await super().get_footprint_share(
            zone=zone,
            lat=lat,
            lon=lon,
            source_zone=source_zone,
            source_lat=source_lat,
            source_lon=source_lon,
            footprint_type=footprint_type,
            scope=scope,
            start=start,
            end=end,
        )

    @adataframe(block="blocks")
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
    ) -> pd.DataFrame:
        """Impact of a destination zone decomposed by origin zone."""
        return await super().get_impact_share(
            zone=zone,
            lat=lat,
            lon=lon,
            source_zone=source_zone,
            source_lat=source_lat,
            source_lon=source_lon,
            impact_type=impact_type,
            scope=scope,
            start=start,
            end=end,
        )

    # -- factors -----------------------------------------------------------

    @adataframe()
    async def get_factors(
        self,
        factor_type: Optional[FactorType] = None,
        scope: Optional[Scope] = None,
        production_type: Optional[ProductionType] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        aggregate: bool = False,
    ) -> pd.DataFrame:
        """Emission/consumption factors used in wattnet's calculations.

        Zone-independent: these are global factors, not per-zone metrics.
        """
        return await super().get_factors(
            factor_type=factor_type,
            scope=scope,
            production_type=production_type,
            start=start,
            end=end,
            aggregate=aggregate,
        )

    # -- status --------------------------------------------------------------

    @adataframe(record=True)
    async def get_status(self) -> pd.DataFrame:
        """Health of the API and all its upstream dependencies."""
        return await super().get_status()

    @adataframe(record=True)
    async def get_status_storage(self) -> pd.DataFrame:
        """Health of the wattnet-storage backend."""
        return await super().get_status_storage()

    @adataframe(record=True)
    async def get_status_entsoe(self) -> pd.DataFrame:
        """Health of the ENTSO-E upstream data provider."""
        return await super().get_status_entsoe()

    @adataframe(record=True)
    async def get_status_elexon(self) -> pd.DataFrame:
        """Health of the Elexon upstream data provider."""
        return await super().get_status_elexon()

    @adataframe(record=True)
    async def get_status_epias(self) -> pd.DataFrame:
        """Health of the EPIAS upstream data provider."""
        return await super().get_status_epias()
