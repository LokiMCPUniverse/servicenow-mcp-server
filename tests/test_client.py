"""Tests for ServiceNow API client."""

import json
from unittest.mock import MagicMock

import httpx
import pytest

from servicenow_mcp.client import ServiceNowClient
from servicenow_mcp.exceptions import (
    ServiceNowAPIError,
    ServiceNowAuthenticationError,
    ServiceNowNotFoundError,
    ServiceNowRateLimitError,
)


class TestServiceNowClient:
    """Test ServiceNow client functionality."""

    @pytest.mark.asyncio
    async def test_client_initialization(self, mock_config):
        """Test client initialization."""
        client = ServiceNowClient(mock_config.servicenow)

        assert client.base_url == "https://test.service-now.com/api/now"
        assert client.config == mock_config.servicenow
        assert client._client is None

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_config):
        """Test async context manager."""
        client = ServiceNowClient(mock_config.servicenow)

        async with client:
            assert client._client is not None
            assert isinstance(client._client, httpx.AsyncClient)

        assert client._client is None

    @pytest.mark.asyncio
    async def test_get_record(self, mock_client, sample_incident):
        """Test getting a single record."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": sample_incident}
        mock_response.raise_for_status = MagicMock()

        mock_client._client.request.return_value = mock_response

        result = await mock_client.get_record("incident", "1234567890abcdef")

        assert result == sample_incident
        mock_client._client.request.assert_called_once_with(
            method="GET",
            url="https://test.service-now.com/api/now/table/incident/1234567890abcdef",
            params={"sysparm_display_value": "false"},
            json=None,
        )

    @pytest.mark.asyncio
    async def test_query_records(self, mock_client, sample_incident):
        """Test querying records."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": [sample_incident]}
        mock_response.raise_for_status = MagicMock()

        mock_client._client.request.return_value = mock_response

        result = await mock_client.query_records(
            "incident",
            query="active=true",
            fields=["number", "short_description"],
            limit=10,
        )

        assert result == [sample_incident]
        mock_client._client.request.assert_called_once_with(
            method="GET",
            url="https://test.service-now.com/api/now/table/incident",
            params={
                "sysparm_limit": 10,
                "sysparm_offset": 0,
                "sysparm_display_value": "false",
                "sysparm_query": "active=true",
                "sysparm_fields": "number,short_description",
            },
            json=None,
        )

    @pytest.mark.asyncio
    async def test_create_record(self, mock_client, sample_incident):
        """Test creating a record."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"result": sample_incident}
        mock_response.raise_for_status = MagicMock()

        mock_client._client.request.return_value = mock_response

        data = {
            "short_description": "Test incident",
            "description": "This is a test incident",
        }

        result = await mock_client.create_record("incident", data)

        assert result == sample_incident
        mock_client._client.request.assert_called_once_with(
            method="POST",
            url="https://test.service-now.com/api/now/table/incident",
            params={"sysparm_display_value": "false"},
            json=data,
        )

    @pytest.mark.asyncio
    async def test_update_record(self, mock_client, sample_incident):
        """Test updating a record."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": sample_incident}
        mock_response.raise_for_status = MagicMock()

        mock_client._client.request.return_value = mock_response

        data = {"state": "2"}

        result = await mock_client.update_record("incident", "1234567890abcdef", data)

        assert result == sample_incident
        mock_client._client.request.assert_called_once_with(
            method="PATCH",
            url="https://test.service-now.com/api/now/table/incident/1234567890abcdef",
            params={"sysparm_display_value": "false"},
            json=data,
        )

    @pytest.mark.asyncio
    async def test_delete_record(self, mock_client):
        """Test deleting a record."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.raise_for_status = MagicMock()

        mock_client._client.request.return_value = mock_response

        result = await mock_client.delete_record("incident", "1234567890abcdef")

        assert result is True
        mock_client._client.request.assert_called_once_with(
            method="DELETE",
            url="https://test.service-now.com/api/now/table/incident/1234567890abcdef",
            params=None,
            json=None,
        )

    @pytest.mark.asyncio
    async def test_authentication_error(self, mock_client):
        """Test authentication error handling."""
        # Mock 401 response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status = MagicMock()

        mock_client._client.request.return_value = mock_response

        with pytest.raises(ServiceNowAuthenticationError):
            await mock_client.get_record("incident", "123")

    @pytest.mark.asyncio
    async def test_not_found_error(self, mock_client):
        """Test not found error handling."""
        # Mock 404 response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status = MagicMock()

        mock_client._client.request.return_value = mock_response

        with pytest.raises(ServiceNowNotFoundError):
            await mock_client.get_record("incident", "123")

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, mock_client):
        """Test rate limit error handling."""
        # Mock 429 response
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.raise_for_status = MagicMock()

        mock_client._client.request.return_value = mock_response

        with pytest.raises(ServiceNowRateLimitError):
            await mock_client.get_record("incident", "123")

    @pytest.mark.asyncio
    async def test_rate_limit_retry(self, mock_client):
        """Test rate limit retry logic."""
        # First call returns 429, second call succeeds
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429

        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"result": {"success": True}}
        mock_response_200.raise_for_status = MagicMock()

        # Mock HTTPStatusError for 429
        http_error = httpx.HTTPStatusError(
            "429 Too Many Requests", request=MagicMock(), response=mock_response_429
        )

        # First call raises HTTPStatusError, second succeeds
        mock_client._client.request.side_effect = [http_error, mock_response_200]

        # Override max_retries for faster test
        mock_client.config.max_retries = 1

        result = await mock_client.get_record("incident", "123")

        assert result == {"success": True}
        assert mock_client._client.request.call_count == 2

    @pytest.mark.asyncio
    async def test_json_decode_error(self, mock_client):
        """Test JSON decode error handling."""
        # Mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)
        mock_response.text = "Invalid JSON"
        mock_response.raise_for_status = MagicMock()

        mock_client._client.request.return_value = mock_response

        with pytest.raises(ServiceNowAPIError, match="Invalid JSON response"):
            await mock_client.get_record("incident", "123")

    @pytest.mark.asyncio
    async def test_specialized_methods(self, mock_client, sample_incident, sample_user):
        """Test specialized methods for common tables."""
        # Mock incident response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": sample_incident}
        mock_response.raise_for_status = MagicMock()

        mock_client._client.request.return_value = mock_response

        # Test get_incident
        result = await mock_client.get_incident("123")
        assert result == sample_incident

        # Test query_incidents
        mock_response.json.return_value = {"result": [sample_incident]}
        result = await mock_client.query_incidents(query="active=true")
        assert result == [sample_incident]

        # Test create_incident
        mock_response.json.return_value = {"result": sample_incident}
        result = await mock_client.create_incident({"short_description": "Test"})
        assert result == sample_incident

        # Test update_incident
        mock_response.json.return_value = {"result": sample_incident}
        result = await mock_client.update_incident("123", {"state": "2"})
        assert result == sample_incident

        # Test user methods
        mock_response.json.return_value = {"result": sample_user}
        result = await mock_client.get_user("user123")
        assert result == sample_user

        # Verify correct tables were used
        calls = mock_client._client.request.call_args_list
        assert "table/incident/123" in str(calls[0])
        assert "table/incident" in str(calls[1])
        assert "table/incident" in str(calls[2])
        assert "table/incident/123" in str(calls[3])
        assert "table/sys_user/user123" in str(calls[4])
