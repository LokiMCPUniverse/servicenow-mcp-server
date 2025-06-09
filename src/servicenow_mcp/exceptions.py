"""Custom exceptions for ServiceNow MCP Server."""


class ServiceNowError(Exception):
    """Base exception for ServiceNow errors."""

    pass


class ServiceNowAPIError(ServiceNowError):
    """Exception raised for API errors."""

    pass


class ServiceNowAuthenticationError(ServiceNowAPIError):
    """Exception raised for authentication errors."""

    pass


class ServiceNowNotFoundError(ServiceNowAPIError):
    """Exception raised when a resource is not found."""

    pass


class ServiceNowRateLimitError(ServiceNowAPIError):
    """Exception raised when rate limit is exceeded."""

    pass


class ServiceNowConfigError(ServiceNowError):
    """Exception raised for configuration errors."""

    pass
