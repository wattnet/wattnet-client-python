"""One-off script that builds examples/quickstart.ipynb from source cells.

Not part of the published package — run manually to regenerate the example
notebook (`python examples/_build_notebook.py`), then execute it with a
valid `WATTNET_TOKEN` set in the environment, e.g.:

    WATTNET_TOKEN=<token> jupyter nbconvert --to notebook --execute \
        --inplace examples/quickstart.ipynb
"""

import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []


def md(text: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text: str) -> None:
    cells.append(nbf.v4.new_code_cell(text))


md("""\
# wattnet-client — quickstart with real data

This notebook exercises every method of `wattnet.client.WattnetClient` against the
**live, production** wattnet API (`https://api.wattnet.eu`) and keeps the real
responses as saved output, so you can see exactly what each call returns without
needing your own credentials just to read it.

To re-run this notebook yourself:

1. Get a bearer token (a pre-issued one, or via a credential's `client_id`/`client_secret` — see below).
2. Set it as an environment variable, **never hardcode it in the notebook**:

   ```bash
   export WATTNET_TOKEN="<your-token>"
   jupyter nbconvert --to notebook --execute --inplace examples/quickstart.ipynb
   ```""")

code("""\
import os

from wattnet.client import WattnetClient, WattnetRawClient

client = WattnetClient(token=os.environ["WATTNET_TOKEN"])
client""")

md("""\
Instead of a static token, you can also authenticate with the `client_id` and
`client_secret` of a wattnet credential — the client fetches and
caches a token for you (refreshing it automatically before it expires):

```python
client = WattnetClient(client_id="<your-client-id>", client_secret="<your-client-secret>")
```

We'll use a fixed 6-hour window for every time-series call below, so the examples
are reproducible and the tables stay a readable size.""")

code("""\
START = "2026-07-15T00:00:00Z"
END = "2026-07-15T06:00:00Z"
ZONE = "ES\"""")

md("## Zones\n\n`get_zones()` — metadata and neighbours for every supported zone.")
code("""\
zones = client.get_zones()
print(zones.shape)
zones.head()""")

md(
    "## Energy metrics\n\n"
    "### Generation\n\n`get_generation()` — electricity generation by production type."
)
code("""\
generation = client.get_generation(zone=ZONE, start=START, end=END)
print(generation.shape)
generation.head()""")

md(
    "Omit `zone` and the same call returns every supported zone in one request, "
    "rather than looping over zone codes yourself. The `zone` column tells the "
    "rows apart:"
)
code("""\
all_zones = client.get_generation(start=START, end=END)
print(all_zones.shape)
print(all_zones["zone"].nunique(), "zones in a single call")
all_zones.head()""")

md("### Load\n\n`get_load()` — total electricity demand.")
code("""\
load = client.get_load(zone=ZONE, start=START, end=END)
print(load.shape)
load.head()""")

md(
    "Every zone-filtered method also accepts a `lat`/`lon` pair instead of a zone "
    "code — the API resolves the coordinate to the zone that contains it, which is "
    "handy when all you have is a site location:"
)
code("""\
by_coord = client.get_load(lat=40.4, lon=-3.7, start=START, end=END)
print(by_coord.shape)
by_coord.head()""")

md(
    "Because `timestamp` arrives as a tz-aware `datetime64[ns, UTC]` column, "
    "standard pandas time-series tooling works with no conversion step — here, "
    "hourly means from the raw resolution:"
)
code("""\
hourly = load.set_index("timestamp").resample("1h").mean(numeric_only=True)
hourly""")

md(
    "Every row also carries `updated_at`, the moment that version of the value was "
    "stored. For long ranges the API can do the averaging itself: `resolution` "
    '(`"15m"`, `"1h"` or `"1d"`, buckets in UTC) returns far fewer rows:'
)
code("""\
daily = client.get_load(zone=ZONE, start="2026-07-01", end="2026-07-15", resolution="1d")
print(daily.shape)
daily.head()""")

md("### Imports\n\n`get_imports()` — electricity imported into the zone, by origin.")
code("""\
imports = client.get_imports(zone=ZONE, start=START, end=END)
print(imports.shape)
imports.head()""")

md(
    "### Exports\n\n`get_exports()` — electricity exported from the zone, by destination."
)
code("""\
exports = client.get_exports(zone=ZONE, start=START, end=END)
print(exports.shape)
exports.head()""")

md("### Mix\n\n`get_mix()` — flow-traced generation mix by production type.")
code("""\
mix = client.get_mix(zone=ZONE, start=START, end=END)
print(mix.shape)
mix.head()""")

md(
    "## Environmental metrics\n\n"
    "### Footprints\n\n`get_footprints()` — carbon/water footprint as a time series."
)
code("""\
footprints = client.get_footprints(zone=ZONE, start=START, end=END)
print(footprints.shape)
footprints.head()""")

md(
    "Set `aggregate=True` to get a single value per footprint type over the window "
    "instead of a time series:"
)
code("""\
footprints_agg = client.get_footprints(zone=ZONE, start=START, end=END, aggregate=True)
footprints_agg""")

md("### Impacts\n\n`get_impacts()` — water impact of electricity consumption.")
code("""\
impacts = client.get_impacts(zone=ZONE, start=START, end=END)
print(impacts.shape)
impacts.head()""")

md(
    "### EnvironmentalScore\n\n`get_environmental_score()` — a single 0-100 sustainability score."
)
code("""\
environmental_score = client.get_environmental_score(zone=ZONE, start=START, end=END)
print(environmental_score.shape)
environmental_score.head()""")

md(
    "## Shares metrics\n\n"
    "### Flow share\n\n`get_flow_share()` — share of this zone's production "
    "exported to each destination zone."
)
code("""\
flow_share = client.get_flow_share(zone=ZONE, start=START, end=END)
print(flow_share.shape)
flow_share.head()""")

md(
    "### Mix share\n\n`get_mix_share()` — share of this zone's mix coming from "
    "each origin zone."
)
code("""\
mix_share = client.get_mix_share(zone=ZONE, start=START, end=END)
print(mix_share.shape)
mix_share.head()""")

md(
    "### Footprint share\n\n`get_footprint_share()` — this zone's footprint "
    "decomposed by origin zone."
)
code("""\
footprint_share = client.get_footprint_share(zone=ZONE, start=START, end=END)
print(footprint_share.shape)
footprint_share.head()""")

md(
    "### Impact share\n\n`get_impact_share()` — this zone's impact decomposed "
    "by origin zone."
)
code("""\
impact_share = client.get_impact_share(zone=ZONE, start=START, end=END)
print(impact_share.shape)
impact_share.head()""")

md(
    "## Factors\n\n`get_factors()` — global emission/consumption factors, "
    "independent of any zone."
)
code("""\
factors = client.get_factors(
    factor_type="carbon", production_type="solar", start=START, end=END
)
print(factors.shape)
factors.head()""")

md(
    "## Status\n\n"
    "`get_status()` and its per-dependency variants report the health of the API "
    "and its upstream providers."
)
code("""\
status = client.get_status()
status""")

md(
    "## Raw JSON access\n\n"
    "`WattnetRawClient` exposes the exact same methods but returns the untouched "
    "JSON payload instead of a DataFrame — useful if you want to handle the nested "
    "structure yourself."
)
code("""\
raw_client = WattnetRawClient(token=os.environ["WATTNET_TOKEN"])
zones_json = raw_client.get_zones()
print(type(zones_json), len(zones_json))
zones_json[0]""")

md(
    "## Error handling\n\n"
    "All errors derive from `wattnet.client.WattnetError`. Misconfiguring the "
    "client (e.g. no auth at all) raises `ConfigurationError` immediately, "
    "without making any request:"
)
code("""\
from wattnet.client import ConfigurationError

try:
    WattnetClient()
except ConfigurationError as exc:
    print(f"ConfigurationError: {exc}")""")

md(
    "Errors coming back from the API itself raise `WattnetAPIError`, which carries "
    "the HTTP `status_code`, the API's own `detail` message and a stable `code` so "
    "you can branch on them instead of parsing strings. Here, a coordinate in the middle of the "
    "Atlantic resolves to no zone at all:"
)
code("""\
from wattnet.client import WattnetAPIError

try:
    client.get_load(lat=0.0, lon=-30.0, start=START, end=END)
except WattnetAPIError as exc:
    print(f"status_code: {exc.status_code}")
    print(f"detail:      {exc.detail}")
    print(f"code:        {exc.code}")""")

md(
    "Note that an *unrecognised zone code* is **not** an error: the API does not "
    "validate zone codes against its zone list, it just filters on them, so you "
    "get a successful response with zero rows. Check `.empty` rather than relying "
    "on an exception:"
)
code("""\
missing = client.get_generation(zone="NOT-A-ZONE", start=START, end=END)
print(f"empty: {missing.empty}  shape: {missing.shape}")""")

md(
    "## Async clients\n\n"
    "For asyncio applications there are `AsyncWattnetClient` (DataFrames) and "
    "`AsyncWattnetRawClient` (raw JSON). They expose the same methods as their "
    "synchronous counterparts, every one of them a coroutine, and are used as "
    "async context managers so the underlying `aiohttp` session is closed for you. "
    "Jupyter supports top-level `await`, so we can call them directly:"
)
code("""\
from wattnet.client import AsyncWattnetClient

async with AsyncWattnetClient(token=os.environ["WATTNET_TOKEN"]) as async_client:
    async_generation = await async_client.get_generation(zone=ZONE, start=START, end=END)
print(async_generation.shape)
async_generation.head()""")

md(
    "Because the calls are coroutines, independent requests can run concurrently "
    "with `asyncio.gather`:"
)
code("""\
import asyncio

from wattnet.client import AsyncWattnetRawClient

async with AsyncWattnetRawClient(token=os.environ["WATTNET_TOKEN"]) as async_raw:
    load, generation = await asyncio.gather(
        async_raw.get_load(zone=ZONE, start=START, end=END),
        async_raw.get_generation(zone=ZONE, start=START, end=END),
    )
print(f"load rows: {len(load)}  generation rows: {len(generation)}")""")

nb["cells"] = cells
nbf.write(nb, "examples/quickstart.ipynb")
print("wrote examples/quickstart.ipynb")
