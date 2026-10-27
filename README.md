<div align="left">
  <picture>
    <source media="(prefers-color-scheme: dark)"
            srcset="https://github.com/wattnet/.github/raw/main/images/wattnet-logo-full-dark-transparent-cropped.png" />
    <source media="(prefers-color-scheme: light)"
            srcset="https://github.com/wattnet/.github/raw/main/images/wattnet-logo-full-light-transparent-cropped.png" />
    <img src="https://github.com/wattnet/.github/raw/main/images/wattnet-logo-full-light-transparent-cropped.png"
         alt="Wattnet Logo"
         width="300" />
  </picture>
</div>

# Python Client

[![CI](https://github.com/wattnet/wattnet-client-python/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/wattnet/wattnet-client-python/actions/workflows/ci.yml)
[![Publish](https://github.com/wattnet/wattnet-client-python/actions/workflows/publish.yml/badge.svg)](https://github.com/wattnet/wattnet-client-python/actions/workflows/publish.yml)
[![Release Please](https://github.com/wattnet/wattnet-client-python/actions/workflows/release-please.yml/badge.svg?branch=main)](https://github.com/wattnet/wattnet-client-python/actions/workflows/release-please.yml)
[![codecov](https://codecov.io/gh/wattnet/wattnet-client-python/graph/badge.svg)](https://codecov.io/gh/wattnet/wattnet-client-python)
[![GitHub stars](https://img.shields.io/github/stars/wattnet/wattnet-client-python?style=social)](https://github.com/wattnet/wattnet-client-python/stargazers)
[![PyPI version](https://img.shields.io/pypi/v/wattnet-client)](https://pypi.org/project/wattnet-client/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/wattnet-client?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/wattnet-client)
[![Python](https://img.shields.io/pypi/pyversions/wattnet-client)](https://pypi.org/project/wattnet-client/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

`wattnet-client` is the official Python client for the [wattnet API](https://github.com/wattnet/wattnet-api). It maps every API endpoint to a client method and hands back a [pandas](https://pandas.pydata.org/) `DataFrame` — no manual HTTP calls or JSON flattening required.

## Features

- **One method per endpoint** — `client.get_generation(...)`, `client.get_footprints(...)`, etc., mirroring the API 1:1.
- **DataFrames by default** — every method returns a tidy `pandas.DataFrame`. Need the raw JSON instead? Use `WattnetRawClient`.
- **Sync and async** — `WattnetClient` and `WattnetRawClient` for scripts and notebooks, `AsyncWattnetClient` and `AsyncWattnetRawClient` for asyncio applications.
- **Two ways to authenticate** — a static bearer token, or the `client_id` and `client_secret` of a wattnet credential; the library fetches and caches tokens for you.
- **Typed, autocomplete-friendly** — zone codes, production types, footprint scopes, etc. are typed for IDE/Jupyter tab-completion.

See [`examples/quickstart.ipynb`](examples/quickstart.ipynb) for every method exercised against the real API, with actual DataFrame outputs saved in the notebook.

## Installation

```bash
pip install wattnet-client
```

### From source

```bash
git clone https://github.com/wattnet/wattnet-client-python.git
cd wattnet-client-python
poetry install
```

## Quickstart

```python
from wattnet.client import WattnetClient

# Option 1: a pre-issued bearer token
client = WattnetClient(token="<your-token>")

# Option 2: a wattnet credential — the client fetches and caches a token for you
client = WattnetClient(client_id="<your-client-id>", client_secret="<your-client-secret>")

# Every call returns a pandas DataFrame
df = client.get_generation(zone="ES", production_type="solar")
df = client.get_footprints(zone="ES", footprint_type="carbon", scope="life-cycle")
df = client.get_environmental_score(zone="ES", aggregate=True, start="2026-01-01", end="2026-02-01")
```

Filter by coordinates instead of a zone code:

```python
df = client.get_load(lat=40.4, lon=-3.7)
```

Every time-series `DataFrame` has a `timestamp` column parsed as a tz-aware
(UTC) `datetime64[ns, UTC]`, ready to plot or resample without any manual
conversion. Omit `zone` (and other filter params) to get every zone back in
a single call instead of querying one at a time.

### Authentication

A credential (`client_id` and `client_secret`) is created in the [developer portal](https://developer.wattnet.eu). The client exchanges it for a bearer token with the OAuth 2.0 `client_credentials` grant the first time it's needed, keeps the token in memory, and renews it once 80 % of its lifetime has passed (but never later than a minute before it expires). If the API still rejects the cached token as expired, the client refreshes it and retries the request once.

```python
client = WattnetClient(client_id="<your-client-id>", client_secret="<your-client-secret>")
```

Read the secret from an environment variable or a secrets manager rather than writing it in code. The token endpoint is discovered from the OpenID Connect issuer (`https://auth.wattnet.eu/realms/wattnet`).

### Raw JSON access

If you need the untouched API response instead of a DataFrame, use `WattnetRawClient` — it exposes the exact same methods:

```python
from wattnet.client import WattnetRawClient

raw = WattnetRawClient(token="<your-token>")
payload = raw.get_generation(zone="ES")  # list[dict], straight from the API
```

### Async client

For asyncio applications (for example the [wattnet Home Assistant integration](https://github.com/wattnet/wattnet-home-assistant)) use `AsyncWattnetRawClient`. It exposes the same methods as `WattnetRawClient`, every one of them a coroutine, and returns raw JSON. It is built on [aiohttp](https://docs.aiohttp.org/) and does not import pandas. If you prefer DataFrames, `AsyncWattnetClient` is its counterpart of `WattnetClient`: the same methods as coroutines returning a `pandas.DataFrame`.

```python
import asyncio

from wattnet.client import AsyncWattnetRawClient


async def main() -> None:
    async with AsyncWattnetRawClient(token="<your-token>") as client:
        zones = await client.get_zones()
        footprints = await client.get_footprints(zone="ES", footprint_type="carbon")


asyncio.run(main())
```

```python
from wattnet.client import AsyncWattnetClient

async with AsyncWattnetClient(token="<your-token>") as client:
    df = await client.get_footprints(zone="ES", footprint_type="carbon")
```

Pass your own `aiohttp.ClientSession` with `session=...` to reuse an existing connection pool. A session you supply is never closed by the client. Authentication, retries, `Retry-After` handling and the token refresh on a 401 behave exactly as in the synchronous clients. 

## Available methods

| Method                                                        | API endpoint          | Description                                                  |
| --------------------------------------------------------------- | ---------------------- | ------------------------------------------------------------- |
| `get_zones()`                                                    | `GET /zones`            | Metadata and neighbours for all supported zones               |
| `get_generation(...)`                                            | `GET /generation`       | Electricity generation by production type                     |
| `get_load(...)`                                                  | `GET /load`             | Total electricity demand                                      |
| `get_imports(...)`                                               | `GET /imports`          | Electricity imports, optionally filtered by origin zone        |
| `get_exports(...)`                                               | `GET /exports`          | Electricity exports, optionally filtered by destination zone   |
| `get_mix(...)`                                                   | `GET /mix`              | Flow-traced generation mix by production type                 |
| `get_footprints(...)`                                            | `GET /footprints`       | Carbon/water footprint of consumption                         |
| `get_impacts(...)`                                               | `GET /impacts`          | Water impact of consumption                                    |
| `get_environmental_score(...)`                                           | `GET /environmental-score`      | EnvironmentalScore (0–100) of consumption                              |
| `get_flow_share(...)`                                            | `GET /flow-share`       | Share of a zone's production exported to each destination      |
| `get_mix_share(...)`                                             | `GET /mix-share`        | Share of a zone's mix coming from each origin                  |
| `get_footprint_share(...)`                                       | `GET /footprint-share`  | Footprint decomposed by origin zone                            |
| `get_impact_share(...)`                                          | `GET /impact-share`     | Impact decomposed by origin zone                               |
| `get_factors(...)`                                               | `GET /factors`          | Global emission/consumption factors                            |
| `get_status()` / `get_status_storage()` / `get_status_entsoe()` / `get_status_elexon()` / `get_status_epias()` | `GET /status[/...]` | Health of the API and its upstream dependencies |

Every method's parameters mirror the corresponding API endpoint's query parameters exactly — see each method's docstring/type hints, or the [wattnet-api docs](https://api.wattnet.eu/docs) for the full parameter reference.

`get_zones()` and `get_factors(...)` are cached in memory per client instance for an hour (they're near-static reference data) — repeated calls within that window don't hit the network again.

## Configuration

| Constructor argument | Environment variable      | Default                                 |
| --------------------- | -------------------------- | ---------------------------------------- |
| `base_url`            | `WATTNET_API_BASE_URL`     | `https://api.wattnet.eu/v1`               |
| `issuer_url`          | `WATTNET_ISSUER_URL`       | `https://auth.wattnet.eu/realms/wattnet`  |
| `token_url`           | `WATTNET_TOKEN_URL`        | read from the issuer's discovery document |

Other constructor options: `session` (bring your own `requests.Session`), `timeout`, `retry_count`, `retry_delay`.

Requests are retried up to `retry_count` times (default 3, waiting `retry_delay` seconds between attempts) on connection/timeout errors and on `429`/`5xx` responses — a `429` waits for the `Retry-After` value the API sends instead of the fixed delay, when present. A `401` always triggers one token refresh + retry, independent of `retry_count`.

`WattnetClient`/`WattnetRawClient` support the context manager protocol, closing
the underlying HTTP session on exit:

```python
with WattnetClient(token="<your-token>") as client:
    df = client.get_zones()
```

`repr(client)` shows the base URL and auth mode (e.g. `WattnetClient(base_url='https://api.wattnet.eu/v1', auth=StaticTokenProvider)`) — never any credentials.

## Error handling

All errors raised by this library derive from `wattnet.client.WattnetError`:

- `ConfigurationError` — the client was instantiated with invalid/incomplete auth arguments.
- `AuthenticationError` — invalid token or credentials.
- `WattnetAPIError` — the API returned a non-2xx response; carries `.status_code` and `.detail`.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for environment setup, code style, and how to run the tests.

## License

This repository is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

See the [LICENSE](LICENSE) file for more details.

## Funding and Acknowledgments

This work was developed within the [GreenDIGIT](https://greendigit-project.eu/) project, funded by the European Union's Horizon Europe research and innovation programme under grant agreement No. [101131207](https://cordis.europa.eu/project/id/101131207), and by the Swiss State Secretariat for Education, Research and Innovation (SERI).

<img src="https://github.com/wattnet/.github/raw/main/images/GreenDIGIT logo color horizontal2.png" alt="GreenDIGIT Logo" width="230" align="right"/>
<img src="https://github.com/wattnet/.github/raw/main/images/EN_FundedbytheEU_RGB_POS.png" alt="EU Funded Logo" width="260" align="left"/>
<img src="https://github.com/wattnet/.github/raw/main/images/Flag_of_Switzerland.svg" alt="Swiss State Secretariat for Education, Research and Innovation (SERI)" height="50" align="left"/>
<br clear="all"/>

##### © 2026 Spanish National Research Council (CSIC). All rights reserved.

