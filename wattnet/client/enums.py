"""Literal type aliases for wattnet-api's enum-like query parameters.

These mirror the valid value sets enforced server-side by
`wattnet.api.utils.validation` — they exist here purely to give IDEs
autocomplete/type-checking on client calls; the server remains the source
of truth and still validates every request.
"""

from typing import Literal

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
