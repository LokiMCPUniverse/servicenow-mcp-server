"""ServiceNow API client implementation."""

import asyncio
import json
from typing import Any, Optional

import httpx
from httpx import Response

from .config import ServiceNowConfig
from .exceptions import (
    ServiceNowAPIError,
    ServiceNowAuthenticationError,
    ServiceNowNotFoundError,
    ServiceNowRateLimitError,
)


class ServiceNowClient:
    """Async client for ServiceNow API interactions."""

    def __init__(self, config: ServiceNowConfig):
        """Initialize ServiceNow client."""
        self.config = config
        self.base_url = f"{config.instance}/api/now"
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def connect(self) -> None:
        """Initialize HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                auth=(self.config.username, self.config.password),
                timeout=self.config.timeout,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> dict[str, Any]:
        """Make an HTTP request to ServiceNow API."""
        if self._client is None:
            await self.connect()

        url = f"{self.base_url}/{endpoint}"

        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=params,
                json=data,
            )

            return self._handle_response(response)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and retry_count < self.config.max_retries:
                # Handle rate limiting with exponential backoff
                wait_time = 2**retry_count
                await asyncio.sleep(wait_time)
                return await self._request(
                    method, endpoint, params, data, retry_count + 1
                )

            raise self._convert_http_error(e) from e

        except httpx.RequestError as e:
            raise ServiceNowAPIError(f"Request failed: {e!s}") from e

    def _handle_response(self, response: Response) -> dict[str, Any]:
        """Handle API response."""
        if response.status_code == 401:
            raise ServiceNowAuthenticationError("Authentication failed")

        if response.status_code == 404:
            raise ServiceNowNotFoundError("Resource not found")

        if response.status_code == 429:
            raise ServiceNowRateLimitError("Rate limit exceeded")

        response.raise_for_status()

        try:
            return response.json()
        except json.JSONDecodeError:
            raise ServiceNowAPIError(
                f"Invalid JSON response: {response.text}"
            ) from None

    def _convert_http_error(self, error: httpx.HTTPStatusError) -> ServiceNowAPIError:
        """Convert HTTP error to ServiceNow error."""
        status_code = error.response.status_code

        if status_code == 401:
            return ServiceNowAuthenticationError("Authentication failed")
        elif status_code == 404:
            return ServiceNowNotFoundError("Resource not found")
        elif status_code == 429:
            return ServiceNowRateLimitError("Rate limit exceeded")
        else:
            return ServiceNowAPIError(f"HTTP {status_code}: {error.response.text}")

    # Table API methods

    async def get_record(
        self,
        table: str,
        sys_id: str,
        fields: Optional[list[str]] = None,
        display_value: str = "false",
    ) -> dict[str, Any]:
        """Get a single record from a table."""
        endpoint = f"table/{table}/{sys_id}"
        params = {"sysparm_display_value": display_value}

        if fields:
            params["sysparm_fields"] = ",".join(fields)

        result = await self._request("GET", endpoint, params=params)
        return result.get("result", {})

    async def query_records(
        self,
        table: str,
        query: Optional[str] = None,
        fields: Optional[list[str]] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = None,
        display_value: str = "false",
    ) -> list[dict[str, Any]]:
        """Query records from a table."""
        endpoint = f"table/{table}"
        params = {
            "sysparm_limit": limit,
            "sysparm_offset": offset,
            "sysparm_display_value": display_value,
        }

        if query:
            params["sysparm_query"] = query

        if fields:
            params["sysparm_fields"] = ",".join(fields)

        if order_by:
            params["sysparm_order_by"] = order_by

        result = await self._request("GET", endpoint, params=params)
        return result.get("result", [])

    async def create_record(
        self,
        table: str,
        data: dict[str, Any],
        display_value: str = "false",
    ) -> dict[str, Any]:
        """Create a new record in a table."""
        endpoint = f"table/{table}"
        params = {"sysparm_display_value": display_value}

        result = await self._request("POST", endpoint, params=params, data=data)
        return result.get("result", {})

    async def update_record(
        self,
        table: str,
        sys_id: str,
        data: dict[str, Any],
        display_value: str = "false",
    ) -> dict[str, Any]:
        """Update an existing record."""
        endpoint = f"table/{table}/{sys_id}"
        params = {"sysparm_display_value": display_value}

        result = await self._request("PATCH", endpoint, params=params, data=data)
        return result.get("result", {})

    async def delete_record(self, table: str, sys_id: str) -> bool:
        """Delete a record from a table."""
        endpoint = f"table/{table}/{sys_id}"

        await self._request("DELETE", endpoint)
        return True

    # Aggregate API methods

    async def get_aggregate(
        self,
        table: str,
        query: Optional[str] = None,
        group_by: Optional[list[str]] = None,
        having: Optional[str] = None,
        aggregate: Optional[list[dict[str, str]]] = None,
    ) -> list[dict[str, Any]]:
        """Get aggregate data from a table."""
        endpoint = f"stats/{table}"
        params = {}

        if query:
            params["sysparm_query"] = query

        if group_by:
            params["sysparm_group_by"] = ",".join(group_by)

        if having:
            params["sysparm_having"] = having

        if aggregate:
            agg_list = []
            for agg in aggregate:
                agg_str = f"{agg['type']}({agg['field']})"
                if "alias" in agg:
                    agg_str += f" as {agg['alias']}"
                agg_list.append(agg_str)
            params["sysparm_aggregate"] = ",".join(agg_list)

        result = await self._request("GET", endpoint, params=params)
        return result.get("result", [])

    # Attachment API methods

    async def get_attachments(
        self,
        table: str,
        sys_id: str,
    ) -> list[dict[str, Any]]:
        """Get attachments for a record."""
        endpoint = "attachment"
        params = {
            "sysparm_query": f"table_name={table}^table_sys_id={sys_id}",
        }

        result = await self._request("GET", endpoint, params=params)
        return result.get("result", [])

    async def upload_attachment(
        self,
        table: str,
        sys_id: str,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> dict[str, Any]:
        """Upload an attachment to a record."""
        endpoint = "attachment/file"
        params = {
            "table_name": table,
            "table_sys_id": sys_id,
            "file_name": filename,
        }

        # For file uploads, we need to use multipart form data
        # This is a simplified version - in production, use proper multipart handling
        headers = {
            "Content-Type": content_type,
        }

        if self._client is None:
            await self.connect()

        url = f"{self.base_url}/{endpoint}"
        response = await self._client.post(
            url,
            params=params,
            content=content,
            headers=headers,
        )

        return self._handle_response(response).get("result", {})

    # Import Set API methods

    async def create_import_set(
        self,
        table: str,
        data: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Create records via import set API."""
        endpoint = f"import/{table}"

        result = await self._request("POST", endpoint, data={"records": data})
        return result.get("result", {})

    # Specialized methods for common tables

    async def get_incident(self, sys_id: str, **kwargs) -> dict[str, Any]:
        """Get an incident by sys_id."""
        return await self.get_record("incident", sys_id, **kwargs)

    async def query_incidents(self, **kwargs) -> list[dict[str, Any]]:
        """Query incidents."""
        return await self.query_records("incident", **kwargs)

    async def create_incident(self, data: dict[str, Any], **kwargs) -> dict[str, Any]:
        """Create a new incident."""
        return await self.create_record("incident", data, **kwargs)

    async def update_incident(
        self, sys_id: str, data: dict[str, Any], **kwargs
    ) -> dict[str, Any]:
        """Update an incident."""
        return await self.update_record("incident", sys_id, data, **kwargs)

    async def get_change_request(self, sys_id: str, **kwargs) -> dict[str, Any]:
        """Get a change request by sys_id."""
        return await self.get_record("change_request", sys_id, **kwargs)

    async def query_change_requests(self, **kwargs) -> list[dict[str, Any]]:
        """Query change requests."""
        return await self.query_records("change_request", **kwargs)

    async def get_user(self, sys_id: str, **kwargs) -> dict[str, Any]:
        """Get a user by sys_id."""
        return await self.get_record("sys_user", sys_id, **kwargs)

    async def query_users(self, **kwargs) -> list[dict[str, Any]]:
        """Query users."""
        return await self.query_records("sys_user", **kwargs)

    async def get_ci(self, sys_id: str, **kwargs) -> dict[str, Any]:
        """Get a configuration item by sys_id."""
        return await self.get_record("cmdb_ci", sys_id, **kwargs)

    async def query_cis(self, **kwargs) -> list[dict[str, Any]]:
        """Query configuration items."""
        return await self.query_records("cmdb_ci", **kwargs)
