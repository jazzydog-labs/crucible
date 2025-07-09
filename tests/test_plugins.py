"""Tests for the plugin system."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Dict
import pytest

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from crucible.plugins.base import (
    CruciblePlugin,
    PluginMetadata,
    PluginContext,
    PluginCapability,
    PluginError,
    PluginLoadError,
    PluginValidationError,
)
from crucible.plugins.loader import PluginLoader
from crucible.plugins.registry import PluginRegistry


class MockPlugin(CruciblePlugin):
    """Mock plugin for testing."""
    
    def __init__(self, name: str = "test_plugin"):
        super().__init__()
        self.name = name
        self.initialized = False
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return mock metadata."""
        return PluginMetadata(
            name=self.name,
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            capabilities=[PluginCapability.PROMPT_PROVIDER],
        )
    
    def initialize(self, context: PluginContext) -> None:
        """Initialize the plugin."""
        self.initialized = True
        self._context = context
    
    def shutdown(self) -> None:
        """Shutdown the plugin."""
        self.initialized = False
    
    def get_prompt_providers(self) -> Dict[str, Any]:
        """Return mock prompt providers."""
        return {
            "test_provider": lambda ctx: f"Test prompt for {ctx.get('topic', 'unknown')}"
        }


class TestPluginMetadata:
    """Test plugin metadata."""
    
    def test_create_metadata(self):
        """Test creating metadata."""
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            capabilities=[PluginCapability.PROMPT_PROVIDER],
            dependencies=["requests"],
        )
        
        assert metadata.name == "test_plugin"
        assert metadata.version == "1.0.0"
        assert metadata.description == "Test plugin"
        assert metadata.author == "Test Author"
        assert metadata.capabilities == [PluginCapability.PROMPT_PROVIDER]
        assert metadata.dependencies == ["requests"]
    
    def test_from_manifest(self):
        """Test loading metadata from manifest."""
        manifest_data = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin",
            "author": "Test Author",
            "capabilities": ["prompt_provider"],
            "dependencies": ["requests"]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(manifest_data, f)
            manifest_path = Path(f.name)
        
        try:
            metadata = PluginMetadata.from_manifest(manifest_path)
            
            assert metadata.name == "test_plugin"
            assert metadata.version == "1.0.0"
            assert metadata.capabilities == [PluginCapability.PROMPT_PROVIDER]
            assert metadata.dependencies == ["requests"]
        finally:
            manifest_path.unlink()
    
    def test_to_dict(self):
        """Test converting metadata to dict."""
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            capabilities=[PluginCapability.PROMPT_PROVIDER],
        )
        
        data = metadata.to_dict()
        
        assert data["name"] == "test_plugin"
        assert data["version"] == "1.0.0"
        assert data["capabilities"] == ["prompt_provider"]


class TestPluginContext:
    """Test plugin context."""
    
    def test_create_context(self):
        """Test creating plugin context."""
        config = {"api_key": "test_key"}
        context = PluginContext(config=config)
        
        assert context.config == config
        assert context.event_bus is None
        assert context.ai_model is None
        assert context.data_dir is None
    
    def test_get_plugin_data_dir(self):
        """Test getting plugin data directory."""
        context = PluginContext(config={})
        
        data_dir = context.get_plugin_data_dir("test_plugin")
        
        assert data_dir.exists()
        assert data_dir.name == "test_plugin"
        assert data_dir.parent.name == "plugins"
        
        # Cleanup
        data_dir.rmdir()
        data_dir.parent.rmdir()
        data_dir.parent.parent.rmdir()


class TestCruciblePlugin:
    """Test the base plugin class."""
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        plugin = MockPlugin()
        context = PluginContext(config={})
        
        assert not plugin.initialized
        
        plugin.initialize(context)
        assert plugin.initialized
        assert plugin._context == context
    
    def test_plugin_shutdown(self):
        """Test plugin shutdown."""
        plugin = MockPlugin()
        context = PluginContext(config={})
        
        plugin.initialize(context)
        assert plugin.initialized
        
        plugin.shutdown()
        assert not plugin.initialized
    
    def test_plugin_metadata(self):
        """Test plugin metadata."""
        plugin = MockPlugin("my_plugin")
        metadata = plugin.metadata
        
        assert metadata.name == "my_plugin"
        assert metadata.version == "1.0.0"
        assert PluginCapability.PROMPT_PROVIDER in metadata.capabilities
    
    def test_plugin_prompt_providers(self):
        """Test plugin prompt providers."""
        plugin = MockPlugin()
        providers = plugin.get_prompt_providers()
        
        assert "test_provider" in providers
        
        provider = providers["test_provider"]
        result = provider({"topic": "testing"})
        assert result == "Test prompt for testing"
    
    def test_default_methods(self):
        """Test default method implementations."""
        plugin = MockPlugin()
        
        assert plugin.get_commands() == []
        assert plugin.get_event_handlers() == {}
        assert plugin.get_ai_adapters() == {}
        assert plugin.get_output_formatters() == {}
        assert plugin.get_workflow_extensions() == {}
        assert plugin.get_storage_backends() == {}
    
    def test_config_validation(self):
        """Test config validation."""
        plugin = MockPlugin()
        
        # Should not raise for empty config
        plugin.validate_config({})
        
        # Should not raise for any config when no schema defined
        plugin.validate_config({"any": "value"})


class TestPluginLoader:
    """Test the plugin loader."""
    
    def test_default_plugin_dirs(self):
        """Test default plugin directories."""
        loader = PluginLoader()
        
        assert isinstance(loader.plugin_dirs, list)
        # Should include user directory
        user_dir = Path.home() / ".crucible" / "plugins"
        # Note: user_dir might not exist, so we can't assert it's in the list
        
    def test_discover_plugins_empty(self):
        """Test discovering plugins with no plugin directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = PluginLoader([Path(temp_dir)])
            plugins = loader.discover_plugins()
            
            assert plugins == {}
    
    def test_discover_plugins_with_manifest(self):
        """Test discovering plugins with manifest files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create plugin directory with manifest
            plugin_dir = temp_path / "test_plugin"
            plugin_dir.mkdir()
            
            manifest_data = {
                "name": "test_plugin",
                "version": "1.0.0",
                "description": "Test plugin",
                "author": "Test Author",
                "capabilities": ["prompt_provider"]
            }
            
            with open(plugin_dir / "manifest.json", 'w') as f:
                json.dump(manifest_data, f)
            
            loader = PluginLoader([temp_path])
            plugins = loader.discover_plugins()
            
            assert "test_plugin" in plugins
            assert plugins["test_plugin"].name == "test_plugin"
            assert plugins["test_plugin"].version == "1.0.0"
    
    def test_load_plugin_not_found(self):
        """Test loading a plugin that doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = PluginLoader([Path(temp_dir)])
            
            with pytest.raises(PluginLoadError, match="Plugin 'nonexistent' not found"):
                loader.load_plugin("nonexistent")
    
    def test_create_plugin_instance(self):
        """Test creating a plugin instance."""
        # This test would require a real plugin file structure
        # For now, we'll test the method signature
        loader = PluginLoader()
        context = PluginContext(config={})
        
        # This will fail because the plugin doesn't exist
        with pytest.raises(PluginLoadError):
            loader.create_plugin_instance("nonexistent", context)


class TestPluginRegistry:
    """Test the plugin registry."""
    
    def test_registry_creation(self):
        """Test creating a plugin registry."""
        registry = PluginRegistry()
        
        assert isinstance(registry.loader, PluginLoader)
        assert registry._plugins == {}
    
    def test_register_plugin_mock(self):
        """Test registering a mock plugin."""
        registry = PluginRegistry()
        
        # Mock the loader to return our mock plugin
        plugin = MockPlugin()
        context = PluginContext(config={})
        
        # We can't easily test the full registration without a real plugin file
        # So we'll test the registry's internal methods
        registry._plugins["test_plugin"] = plugin
        plugin.initialize(context)
        
        assert "test_plugin" in registry._plugins
        assert registry.get_plugin("test_plugin") == plugin
    
    def test_get_plugins_by_capability(self):
        """Test getting plugins by capability."""
        registry = PluginRegistry()
        
        # Add a mock plugin
        plugin = MockPlugin()
        registry._plugins["test_plugin"] = plugin
        registry._capabilities[PluginCapability.PROMPT_PROVIDER] = ["test_plugin"]
        
        plugins = registry.get_plugins_by_capability(PluginCapability.PROMPT_PROVIDER)
        
        assert len(plugins) == 1
        assert plugins[0] == plugin
    
    def test_get_plugins_by_capability_empty(self):
        """Test getting plugins by capability when none exist."""
        registry = PluginRegistry()
        
        plugins = registry.get_plugins_by_capability(PluginCapability.AI_ADAPTER)
        
        assert plugins == []
    
    def test_list_plugins(self):
        """Test listing all plugins."""
        registry = PluginRegistry()
        
        # Add a mock plugin
        plugin = MockPlugin()
        registry._plugins["test_plugin"] = plugin
        
        plugins = registry.list_plugins()
        
        assert "test_plugin" in plugins
        assert plugins["test_plugin"]["metadata"]["name"] == "test_plugin"
    
    def test_get_all_formatters(self):
        """Test getting all formatters."""
        registry = PluginRegistry()
        
        # Should return empty dict initially
        formatters = registry.get_all_output_formatters()
        assert formatters == {}
    
    def test_get_all_providers(self):
        """Test getting all providers."""
        registry = PluginRegistry()
        
        # Should return empty dict initially
        providers = registry.get_all_prompt_providers()
        assert providers == {}
    
    def test_emit_event(self):
        """Test emitting events."""
        registry = PluginRegistry()
        
        # Mock event handler
        events_received = []
        
        def mock_handler(payload):
            events_received.append(payload)
        
        # Register handler
        registry._event_handlers["test_event"] = [mock_handler]
        
        # Emit event
        registry.emit_event("test_event", {"data": "test"})
        
        assert len(events_received) == 1
        assert events_received[0] == {"data": "test"}
    
    def test_emit_event_with_error(self):
        """Test emitting events with handler errors."""
        registry = PluginRegistry()
        
        def failing_handler(payload):
            raise ValueError("Test error")
        
        registry._event_handlers["test_event"] = [failing_handler]
        
        # Should not raise, just log the error
        registry.emit_event("test_event", {"data": "test"})
    
    def test_shutdown_all(self):
        """Test shutting down all plugins."""
        registry = PluginRegistry()
        
        # Add mock plugin
        plugin = MockPlugin()
        plugin.initialize(PluginContext(config={}))
        registry._plugins["test_plugin"] = plugin
        
        registry.shutdown_all()
        
        assert not plugin.initialized
        assert registry._plugins == {}


if __name__ == "__main__":
    pytest.main([__file__])