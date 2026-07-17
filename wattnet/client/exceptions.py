"""Exceptions raised by the wattnet client."""

from typing import Optional


class WattnetError(Exception):
    """Base class for all errors raised by this library."""


class ConfigurationError(WattnetError):
    """Raised when a client is instantiated with invalid or incomplete auth config."""


class AuthenticationError(WattnetError):
    """Raised when a token or credentials are rejected by the token or API service."""


class WattnetAPIError(WattnetError):
    """Raised when the wattnet API returns a non-2xx response.

    :ivar status_code: HTTP status code returned by the API.
    :ivar detail: The `detail` message from the API's JSON error body, if any.
    """

    def __init__(
        self, message: str, status_code: int, detail: Optional[str] = None
    ) -> None:
        """Store the error message alongside the HTTP status code and detail."""
        super().__init__(message, status_code, detail)
        self.status_code = status_code
        self.detail = detail
