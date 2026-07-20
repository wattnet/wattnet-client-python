"""Literal type aliases for wattnet-api's enum-like query parameters.

These mirror the value sets accepted server-side — the enum-like parameters
from `wattnet.api.utils.validation`, and zone codes from the API's zone
data files. They exist purely to give IDEs autocomplete/type-checking on
client calls; the server remains the source of truth and still validates
every request.
"""

from typing import Literal, Union

#: Zone codes known to the client at release time, mirroring
#: `wattnet-api`'s `data/zones/entsoe_full_zones.yaml`.
#:
#: Deliberately widened with `str` rather than left as a bare `Literal`: the
#: API gains zones independently of this package's release cycle, and a strict
#: `Literal` would make type checkers reject a zone the server already serves
#: — failing users' builds on valid code until a new client is published.
#: Widening keeps editor autocomplete for known zones while accepting any
#: string, so an out-of-date list degrades discoverability, never correctness.
#: `get_zones()` remains the runtime source of truth.
Zone = Union[
    Literal[
        "AL", "AM", "AT", "AZ", "BA", "BE", "BG", "BY", "CH", "CY",
        "CZ", "DE", "DK1", "DK2", "EE", "ES", "FI", "FR", "GB", "GE",
        "GR", "HR", "HU", "IE", "IT_CALABRIA", "IT_CNORTH", "IT_CSOUTH",
        "IT_NORTH", "IT_SARDINIA", "IT_SICILY", "IT_SOUTH", "LT", "LU",
        "LV", "MD", "ME", "MK", "MT", "NIE", "NL", "NO1", "NO2", "NO3",
        "NO4", "NO5", "PL", "PT", "RO", "RS", "RU", "RU_KGD", "SE1",
        "SE2", "SE3", "SE4", "SI", "SK", "TR", "UA", "XK",
    ],
    str,
]

ProductionType = Literal[
    "biomass",
    "coal",
    "gas",
    "geothermal",
    "hydro_reservoir",
    "hydro_river",
    "hydro_pumped_storage",
    "marine",
    "nuclear",
    "oil",
    "other",
    "other_renewable",
    "solar",
    "waste",
    "wind_offshore",
    "wind_onshore",
]

FootprintType = Literal["carbon", "water"]
FactorType = Literal["carbon", "water"]
ImpactType = Literal["water"]
Scope = Literal["operational", "life-cycle"]
