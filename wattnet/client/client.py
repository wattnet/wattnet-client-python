"""DataFrame-returning client for the wattnet API — the friendly default.

Every method mirrors `WattnetRawClient`'s method of the same name, but
returns a `pandas.DataFrame` instead of raw JSON. Use `WattnetRawClient`
directly only if you specifically need the untouched JSON payload.
"""

from datetime import datetime
from typing import Optional

import pandas as pd

from wattnet.client.decorators import dataframe
from wattnet.client.enums import (
    FactorType,
    FootprintType,
    ImpactType,
    ProductionType,
    Resolution,
    Scope,
    Zone,
)
from wattnet.client.raw_client import WattnetRawClient


class WattnetClient(WattnetRawClient):
    """Query the wattnet API and get pandas DataFrames back.

    client = WattnetClient(token="...")
    # or: client = WattnetClient(client_id="...", client_secret="...")

    df = client.get_generation(zone="ES", start=..., end=...)
    """

    # -- zones -----------------------------------------------------------

    @dataframe()
    def get_zones(self) -> pd.DataFrame:
        """List all configured zones with their metadata and neighbours."""
        return super().get_zones()

    # -- energy metrics --------------------------------------------------

    @dataframe(block="production")
    def get_generation(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        production_type: Optional[ProductionType] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        resolution: Optional[Resolution] = None,
    ) -> pd.DataFrame:
        """Electricity generation by production type for a zone or coordinate."""
        return super().get_generation(
            zone=zone,
            lat=lat,
            lon=lon,
            production_type=production_type,
            start=start,
            end=end,
            resolution=resolution,
        )

    @dataframe(block="blocks")
    def get_load(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        resolution: Optional[Resolution] = None,
    ) -> pd.DataFrame:
        """Total electricity demand for a zone or coordinate."""
        return super().get_load(
            zone=zone,
            lat=lat,
            lon=lon,
            start=start,
            end=end,
            resolution=resolution,
        )

    @dataframe(block="imports")
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
    ) -> pd.DataFrame:
        """Electricity imports into a zone, optionally filtered by origin zone."""
        return super().get_imports(
            zone=zone,
            lat=lat,
            lon=lon,
            source_zone=source_zone,
            source_lat=source_lat,
            source_lon=source_lon,
            start=start,
            end=end,
            resolution=resolution,
        )

    @dataframe(block="exports")
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
    ) -> pd.DataFrame:
        """Electricity exports from a zone, optionally filtered by destination."""
        return super().get_exports(
            zone=zone,
            lat=lat,
            lon=lon,
            destination_zone=destination_zone,
            destination_lat=destination_lat,
            destination_lon=destination_lon,
            start=start,
            end=end,
            resolution=resolution,
        )

    @dataframe(block="production")
    def get_mix(
        self,
        zone: Optional[Zone] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        production_type: Optional[ProductionType] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        resolution: Optional[Resolution] = None,
    ) -> pd.DataFrame:
        """Return the flow-traced generation mix by production type for a zone."""
        return super().get_mix(
            zone=zone,
            lat=lat,
            lon=lon,
            production_type=production_type,
            start=start,
            end=end,
            resolution=resolution,
        )

    # -- environmental metrics -----------------------------------------

    @dataframe()
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
    ) -> pd.DataFrame:
        """Carbon/water footprint of electricity consumption in a zone.

        Set `aggregate=True` (with `start`/`end` required) for a single
        aggregated value per zone/series instead of a time series.
        """
        return super().get_footprints(
            zone=zone,
            lat=lat,
            lon=lon,
            footprint_type=footprint_type,
            scope=scope,
            start=start,
            end=end,
            aggregate=aggregate,
            use_global=use_global,
            resolution=resolution,
        )

    @dataframe()
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
    ) -> pd.DataFrame:
        """Water impact of electricity consumption in a zone."""
        return super().get_impacts(
            zone=zone,
            lat=lat,
            lon=lon,
            impact_type=impact_type,
            scope=scope,
            start=start,
            end=end,
            aggregate=aggregate,
            use_global=use_global,
            resolution=resolution,
        )

    @dataframe()
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
    ) -> pd.DataFrame:
        """Return the EnvironmentalScore (0-100) of electricity use in a zone."""
        return super().get_environmental_score(
            zone=zone,
            lat=lat,
            lon=lon,
            scope=scope,
            start=start,
            end=end,
            aggregate=aggregate,
            use_global=use_global,
            resolution=resolution,
        )

    # -- shares metrics --------------------------------------------------

    @dataframe(block="flows")
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
    ) -> pd.DataFrame:
        """Share of an origin zone's production exported to each destination."""
        return super().get_flow_share(
            zone=zone,
            lat=lat,
            lon=lon,
            destination_zone=destination_zone,
            destination_lat=destination_lat,
            destination_lon=destination_lon,
            start=start,
            end=end,
        )

    @dataframe(block="shares")
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
    ) -> pd.DataFrame:
        """Share of a destination zone's mix coming from each origin zone."""
        return super().get_mix_share(
            zone=zone,
            lat=lat,
            lon=lon,
            origin_zone=origin_zone,
            origin_lat=origin_lat,
            origin_lon=origin_lon,
            start=start,
            end=end,
        )

    @dataframe(block="blocks")
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
    ) -> pd.DataFrame:
        """Footprint of a destination zone decomposed by origin zone."""
        return super().get_footprint_share(
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

    @dataframe(block="blocks")
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
    ) -> pd.DataFrame:
        """Impact of a destination zone decomposed by origin zone."""
        return super().get_impact_share(
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

    @dataframe()
    def get_factors(
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
        return super().get_factors(
            factor_type=factor_type,
            scope=scope,
            production_type=production_type,
            start=start,
            end=end,
            aggregate=aggregate,
        )

    # -- status --------------------------------------------------------------

    @dataframe(record=True)
    def get_status(self) -> pd.DataFrame:
        """Health of the API and all its upstream dependencies."""
        return super().get_status()

    @dataframe(record=True)
    def get_status_storage(self) -> pd.DataFrame:
        """Health of the wattnet-storage backend."""
        return super().get_status_storage()

    @dataframe(record=True)
    def get_status_entsoe(self) -> pd.DataFrame:
        """Health of the ENTSO-E upstream data provider."""
        return super().get_status_entsoe()

    @dataframe(record=True)
    def get_status_elexon(self) -> pd.DataFrame:
        """Health of the Elexon upstream data provider."""
        return super().get_status_elexon()

    @dataframe(record=True)
    def get_status_epias(self) -> pd.DataFrame:
        """Health of the EPIAS upstream data provider."""
        return super().get_status_epias()
