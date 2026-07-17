"""Default configuration for the wattnet client.

Defaults are inferred from the wattnet-api documentation (base URL) and the
token-issuer's `root_path` (token URL); override them via constructor
arguments or the environment variables below if your deployment differs.
"""

import os

DEFAULT_BASE_URL = os.environ.get("WATTNET_API_BASE_URL", "https://api.wattnet.eu/v1")
DEFAULT_TOKEN_URL = os.environ.get(
    "WATTNET_TOKEN_URL", "https://api.wattnet.eu/token-request"
)

DEFAULT_TIMEOUT = 30.0
DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_DELAY = 1.0

# HTTP status codes worth retrying: 429 (rate limited) and the 5xx codes that
# typically indicate a transient upstream/server problem rather than a
# request the client will never be able to satisfy.
RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})

# Safety margin subtracted from a token's `expires_at` before it is
# considered stale, to avoid racing an in-flight request against expiry.
TOKEN_EXPIRY_SAFETY_MARGIN_SECONDS = 60

# How long zones/factors responses are cached before being refetched — both
# are near-static reference data that changes on the order of weeks, not
# per-request.
DEFAULT_STATIC_CACHE_TTL_SECONDS = 3600.0
