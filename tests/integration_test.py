#!/usr/bin/env python3
"""Integration test script for ServiceNow MCP Server."""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        import servicenow_mcp
        from servicenow_mcp.client import ServiceNowClient
        from servicenow_mcp.config import Config, ConfigManager, ServiceNowConfig
        from servicenow_mcp.server import ServiceNowMCPServer
        from servicenow_mcp.tools import ToolRegistry
        from servicenow_mcp.exceptions import ServiceNowError
        print("✓ All modules imported successfully")
        print(f"✓ Package version: {servicenow_mcp.__version__}")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_config():
    """Test configuration management."""
    print("\nTesting configuration...")
    try:
        from servicenow_mcp.config import ServiceNowConfig
        
        # Test subdomain only
        config = ServiceNowConfig(instance='test', username='u', password='p')
        assert config.instance == 'https://test.service-now.com', f"Expected https://test.service-now.com, got {config.instance}"
        print("✓ Subdomain-only instance validated")
        
        # Test full domain
        config = ServiceNowConfig(instance='test.service-now.com', username='u', password='p')
        assert config.instance == 'https://test.service-now.com', f"Expected https://test.service-now.com, got {config.instance}"
        print("✓ Full domain instance validated")
        
        # Test full URL
        config = ServiceNowConfig(instance='https://test.service-now.com', username='u', password='p')
        assert config.instance == 'https://test.service-now.com', f"Expected https://test.service-now.com, got {config.instance}"
        print("✓ Full URL instance validated")
        
        # Test trailing slash removal
        config = ServiceNowConfig(instance='https://test.service-now.com/', username='u', password='p')
        assert config.instance == 'https://test.service-now.com', f"Expected https://test.service-now.com, got {config.instance}"
        print("✓ Trailing slash removal validated")
        
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_client():
    """Test client initialization."""
    print("\nTesting client...")
    try:
        from servicenow_mcp.config import ServiceNowConfig
        from servicenow_mcp.client import ServiceNowClient
        
        config = ServiceNowConfig(
            instance='test-instance',
            username='test_user',
            password='test_pass'
        )
        client = ServiceNowClient(config)
        
        assert client.base_url == 'https://test-instance.service-now.com/api/now', \
            f"Expected https://test-instance.service-now.com/api/now, got {client.base_url}"
        print("✓ Client initialized successfully")
        print(f"✓ Base URL: {client.base_url}")
        
        return True
    except Exception as e:
        print(f"✗ Client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_server():
    """Test server initialization."""
    print("\nTesting server...")
    try:
        from servicenow_mcp.config import Config, ServiceNowConfig, FeaturesConfig
        from servicenow_mcp.server import ServiceNowMCPServer
        
        config = Config(
            servicenow=ServiceNowConfig(
                instance='test-instance',
                username='test_user',
                password='test_pass'
            ),
            features=FeaturesConfig()
        )
        
        server = ServiceNowMCPServer(config)
        
        print("✓ Server initialized successfully")
        print(f"✓ Instance: {server.config.servicenow.instance}")
        
        tools = server.tools.get_enabled_tools()
        print(f"✓ Enabled tools: {len(tools)}")
        
        # Verify some essential tools are present
        tool_names = [tool.name for tool in tools]
        essential_tools = ['query_table', 'incident_create', 'ci_search']
        for tool in essential_tools:
            assert tool in tool_names, f"Essential tool '{tool}' not found"
        print(f"✓ Essential tools present: {', '.join(essential_tools)}")
        
        return True
    except Exception as e:
        print(f"✗ Server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tools():
    """Test tool registry."""
    print("\nTesting tools...")
    try:
        from servicenow_mcp.config import FeaturesConfig
        from servicenow_mcp.tools import ToolRegistry
        
        # Test with all features enabled
        features = FeaturesConfig()
        registry = ToolRegistry(features)
        
        tools = registry.get_enabled_tools()
        print(f"✓ Tool registry initialized with {len(tools)} tools")
        
        # Test with some features disabled
        features_partial = FeaturesConfig(
            incident_management=False,
            custom_tables=False
        )
        registry_partial = ToolRegistry(features_partial)
        
        tools_partial = registry_partial.get_enabled_tools()
        print(f"✓ Partial feature set: {len(tools_partial)} tools")
        
        assert len(tools_partial) < len(tools), "Partial tools should be fewer than all tools"
        print("✓ Feature flag filtering works correctly")
        
        return True
    except Exception as e:
        print(f"✗ Tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("ServiceNow MCP Server - Integration Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config,
        test_client,
        test_server,
        test_tools,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    print(f"Passed: {sum(results)}/{len(results)}")
    print(f"Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n✓ All integration tests passed!")
        return 0
    else:
        print("\n✗ Some integration tests failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
