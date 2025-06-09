"""Pytest configuration and fixtures."""

from unittest.mock import AsyncMock

import pytest

from servicenow_mcp.client import ServiceNowClient
from servicenow_mcp.config import Config, FeaturesConfig, ServiceNowConfig


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    return Config(
        servicenow=ServiceNowConfig(
            instance="https://test.service-now.com",
            username="test_user",
            password="test_pass",
            api_version="v2",
            timeout=30,
            max_retries=3,
        ),
        features=FeaturesConfig(
            incident_management=True,
            change_management=True,
            problem_management=True,
            service_catalog=True,
            knowledge_base=True,
            user_management=True,
            cmdb=True,
            custom_tables=True,
        ),
    )


@pytest.fixture
def mock_client(mock_config):
    """Create a mock ServiceNow client."""
    client = ServiceNowClient(mock_config.servicenow)
    # Mock the HTTP client
    client._client = AsyncMock()
    return client


@pytest.fixture
def sample_incident():
    """Sample incident data."""
    return {
        "sys_id": "1234567890abcdef",
        "number": "INC0000001",
        "short_description": "Test incident",
        "description": "This is a test incident",
        "state": "1",
        "priority": "3",
        "urgency": "3",
        "impact": "3",
        "assigned_to": {"value": "user123", "display_value": "John Doe"},
        "assignment_group": {"value": "group123", "display_value": "IT Support"},
    }


@pytest.fixture
def sample_user():
    """Sample user data."""
    return {
        "sys_id": "user123",
        "user_name": "john.doe",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "active": "true",
        "department": {"value": "dept123", "display_value": "Information Technology"},
    }


@pytest.fixture
def sample_ci():
    """Sample configuration item data."""
    return {
        "sys_id": "ci123",
        "name": "PROD-WEB-01",
        "sys_class_name": "cmdb_ci_server",
        "operational_status": "1",
        "u_environment": "production",
        "serial_number": "SN123456",
        "ip_address": "192.168.1.100",
    }
