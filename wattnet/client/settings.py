"""Default configuration for the wattnet client.

Defaults are inferred from the wattnet-api documentation (base URL) and the
OpenID Connect issuer of the wattnet realm; override them via constructor
arguments or the environment variables below if your deployment differs.
"""

import os

DEFAULT_BASE_URL = os.environ.get("WATTNET_API_BASE_URL", "https://api.wattnet.eu/v1")
# The token endpoint is read from the issuer's OpenID Connect discovery
# document; `WATTNET_TOKEN_URL` skips the discovery and uses that URL directly.
DEFAULT_ISSUER_URL = os.environ.get(
    "WATTNET_ISSUER_URL", "https://auth.wattnet.eu/realms/wattnet"
)
DEFAULT_TOKEN_URL = os.environ.get("WATTNET_TOKEN_URL")

DEFAULT_TIMEOUT = 30.0
DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_DELAY = 1.0

# HTTP status codes worth retrying: 429 (rate limited) and the 5xx codes that
# typically indicate a transient upstream/server problem rather than a
# request the client will never be able to satisfy.
RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})

# A token is renewed once this fraction of its `expires_in` has elapsed, but
# never later than this many seconds before it expires.
TOKEN_RENEW_FRACTION = 0.8
TOKEN_MIN_MARGIN_SECONDS = 60

# How long zones/factors responses are cached before being refetched — both
# are near-static reference data that changes on the order of weeks, not
# per-request.
DEFAULT_STATIC_CACHE_TTL_SECONDS = 3600.0
