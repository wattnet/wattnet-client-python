"""Python client for the wattnet API.

from wattnet.client import WattnetClient

client = WattnetClient(token="...")
# or: client = WattnetClient(email="you@example.com", password="...")

df = client.get_generation(zone="ES")

For asyncio applications use `AsyncWattnetClient` (DataFrames) or
`AsyncWattnetRawClient` (raw JSON, no pandas).
"""

from importlib.metadata import version
from typing import TYPE_CHECKING, Any

from wattnet.client.async_auth import async_register
from wattnet.client.async_raw_client import AsyncWattnetRawClient
from wattnet.client.auth import register
from wattnet.client.exceptions import (
    AuthenticationError,
    ConfigurationError,
    WattnetAPIError,
    WattnetError,
)
from wattnet.client.raw_client import WattnetRawClient

__version__ = version("wattnet-client")

if TYPE_CHECKING:  # pragma: no cover
    from wattnet.client.async_client import AsyncWattnetClient
    from wattnet.client.client import WattnetClient


def __getattr__(name: str) -> Any:
    """Import the DataFrame clients lazily so pandas is only loaded when used."""
    if name == "WattnetClient":
        from wattnet.client.client import WattnetClient

        return WattnetClient
    if name == "AsyncWattnetClient":
        from wattnet.client.async_client import AsyncWattnetClient

        return AsyncWattnetClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "__version__",
    "WattnetClient",
    "WattnetRawClient",
    "AsyncWattnetClient",
    "AsyncWattnetRawClient",
    "register",
    "async_register",
    "WattnetError",
    "AuthenticationError",
    "WattnetAPIError",
    "ConfigurationError",
]
