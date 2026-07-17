"""Python client for the wattnet API.

from wattnet.client import WattnetClient

client = WattnetClient(token="...")
# or: client = WattnetClient(email="you@example.com", password="...")

df = client.get_generation(zone="ES")
"""

from wattnet.client.auth import register
from wattnet.client.client import WattnetClient
from wattnet.client.exceptions import (
    AuthenticationError,
    ConfigurationError,
    WattnetAPIError,
    WattnetError,
)
from wattnet.client.raw_client import WattnetRawClient

__version__ = "0.1.0"

__all__ = [
    "WattnetClient",
    "WattnetRawClient",
    "register",
    "WattnetError",
    "AuthenticationError",
    "WattnetAPIError",
    "ConfigurationError",
]
