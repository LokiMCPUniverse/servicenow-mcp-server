"""Tests for configuration management."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from servicenow_mcp.config import ConfigManager, ServiceNowConfig


class TestServiceNowConfig:
    """Test ServiceNowConfig model."""

    def test_instance_validation_with_full_url(self):
        """Test instance URL validation with full URL."""
        config = ServiceNowConfig(
            instance="https://test.service-now.com", username="user", password="pass"
        )
        assert config.instance == "https://test.service-now.com"

    def test_instance_validation_with_subdomain(self):
        """Test instance URL validation with subdomain only."""
        config = ServiceNowConfig(instance="test", username="user", password="pass")
        assert config.instance == "https://test.service-now.com"

    def test_instance_validation_removes_trailing_slash(self):
        """Test that trailing slashes are removed from instance URL."""
        config = ServiceNowConfig(
            instance="https://test.service-now.com/", username="user", password="pass"
        )
        assert config.instance == "https://test.service-now.com"

    def test_instance_validation_empty(self):
        """Test that empty instance raises error."""
        with pytest.raises(ValueError, match="ServiceNow instance cannot be empty"):
            ServiceNowConfig(instance="", username="user", password="pass")


class TestConfigManager:
    """Test ConfigManager functionality."""

    def test_load_default_config(self):
        """Test loading default configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            # Create default config
            default_config = {
                "servicenow": {
                    "instance": "default",
                    "username": "default_user",
                    "password": "default_pass",
                }
            }

            with open(config_dir / "default.json", "w") as f:
                json.dump(default_config, f)

            manager = ConfigManager(config_dir)
            config = manager.load()

            assert config.servicenow.instance == "https://default.service-now.com"
            assert config.servicenow.username == "default_user"
            assert config.servicenow.password == "default_pass"

    def test_local_config_override(self):
        """Test that local config overrides default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            # Create default config
            default_config = {
                "servicenow": {
                    "instance": "default",
                    "username": "default_user",
                    "password": "default_pass",
                }
            }

            # Create local config with override
            local_config = {"servicenow": {"username": "local_user"}}

            with open(config_dir / "default.json", "w") as f:
                json.dump(default_config, f)

            with open(config_dir / "local.json", "w") as f:
                json.dump(local_config, f)

            manager = ConfigManager(config_dir)
            config = manager.load()

            assert config.servicenow.instance == "https://default.service-now.com"
            assert config.servicenow.username == "local_user"  # Overridden
            assert config.servicenow.password == "default_pass"

    def test_env_var_override(self):
        """Test that environment variables override config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            # Create default config
            default_config = {
                "servicenow": {
                    "instance": "default",
                    "username": "default_user",
                    "password": "default_pass",
                    "timeout": 30,
                }
            }

            with open(config_dir / "default.json", "w") as f:
                json.dump(default_config, f)

            # Set environment variables
            os.environ["SERVICENOW_INSTANCE"] = "env-instance"
            os.environ["SERVICENOW_USERNAME"] = "env_user"
            os.environ["SERVICENOW_TIMEOUT"] = "60"

            try:
                manager = ConfigManager(config_dir)
                config = manager.load()

                assert (
                    config.servicenow.instance == "https://env-instance.service-now.com"
                )
                assert config.servicenow.username == "env_user"
                assert config.servicenow.password == "default_pass"  # Not overridden
                assert config.servicenow.timeout == 60  # Converted to int
            finally:
                # Clean up env vars
                del os.environ["SERVICENOW_INSTANCE"]
                del os.environ["SERVICENOW_USERNAME"]
                del os.environ["SERVICENOW_TIMEOUT"]

    def test_feature_flags_env_override(self):
        """Test feature flags can be overridden by environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            # Create default config with all features enabled
            default_config = {
                "servicenow": {
                    "instance": "test",
                    "username": "user",
                    "password": "pass",
                },
                "features": {
                    "incident_management": True,
                    "change_management": True,
                    "cmdb": True,
                },
            }

            with open(config_dir / "default.json", "w") as f:
                json.dump(default_config, f)

            # Disable some features via env
            os.environ["SERVICENOW_FEATURE_INCIDENT_MANAGEMENT"] = "false"
            os.environ["SERVICENOW_FEATURE_CMDB"] = "0"

            try:
                manager = ConfigManager(config_dir)
                config = manager.load()

                assert config.features.incident_management is False
                assert config.features.change_management is True
                assert config.features.cmdb is False
            finally:
                del os.environ["SERVICENOW_FEATURE_INCIDENT_MANAGEMENT"]
                del os.environ["SERVICENOW_FEATURE_CMDB"]

    def test_deep_merge(self):
        """Test deep merge functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            # Create default config
            default_config = {
                "servicenow": {
                    "instance": "default",
                    "username": "default_user",
                    "password": "default_pass",
                },
                "features": {"incident_management": True, "change_management": True},
                "logging": {"level": "INFO", "format": "json"},
            }

            # Create local config with partial overrides
            local_config = {
                "servicenow": {"username": "local_user"},
                "features": {"incident_management": False, "cmdb": True},
                "logging": {"level": "DEBUG"},
            }

            with open(config_dir / "default.json", "w") as f:
                json.dump(default_config, f)

            with open(config_dir / "local.json", "w") as f:
                json.dump(local_config, f)

            manager = ConfigManager(config_dir)
            config = manager.load()

            # Check merged values
            assert config.servicenow.username == "local_user"
            assert config.servicenow.password == "default_pass"
            assert config.features.incident_management is False
            assert config.features.change_management is True
            assert config.features.cmdb is True
            assert config.logging.level == "DEBUG"
            assert config.logging.format == "json"
