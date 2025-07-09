"""Plugin registry for managing active plugins and their capabilities."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Set, Type
import logging
from collections import defaultdict

from .base import (
    CruciblePlugin,
    PluginCapability,
    PluginContext,
    PluginError,
)
from .loader import PluginLoader


logger = logging.getLogger(__name__)


class PluginRegistry:
    """Registry for managing loaded plugins and accessing their capabilities."""
    
    def __init__(self, loader: Optional[PluginLoader] = None) -> None:
        """Initialize the plugin registry.
        
        Args:
            loader: Plugin loader instance
        """
        self.loader = loader or PluginLoader()
        self._plugins: Dict[str, CruciblePlugin] = {}
        self._capabilities: Dict[PluginCapability, List[str]] = defaultdict(list)
        self._commands: Dict[str, Dict[str, Any]] = {}
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._prompt_providers: Dict[str, Callable] = {}
        self._ai_adapters: Dict[str, Type] = {}
        self._output_formatters: Dict[str, Callable] = {}
        self._workflow_extensions: Dict[str, Callable] = {}
        self._storage_backends: Dict[str, Type] = {}
    
    def register_plugin(
        self,
        plugin_name: str,
        context: PluginContext,
        auto_enable: bool = True
    ) -> CruciblePlugin:
        """Register a plugin with the registry.
        
        Args:
            plugin_name: Name of the plugin to register
            context: Plugin context
            auto_enable: Whether to automatically enable the plugin
            
        Returns:
            Registered plugin instance
        """
        if plugin_name in self._plugins:
            logger.warning(f"Plugin '{plugin_name}' is already registered")
            return self._plugins[plugin_name]
        
        # Create plugin instance
        plugin = self.loader.create_plugin_instance(plugin_name, context)
        
        # Store the plugin
        self._plugins[plugin_name] = plugin
        
        # Track capabilities
        for capability in plugin.metadata.capabilities:
            self._capabilities[capability].append(plugin_name)
        
        if auto_enable:
            self.enable_plugin(plugin_name)
        
        logger.info(f"Registered plugin: {plugin_name}")
        return plugin
    
    def enable_plugin(self, plugin_name: str) -> None:
        """Enable a registered plugin.
        
        Args:
            plugin_name: Name of the plugin to enable
        """
        if plugin_name not in self._plugins:
            raise PluginError(f"Plugin '{plugin_name}' not registered")
        
        plugin = self._plugins[plugin_name]
        
        # Register commands
        for command in plugin.get_commands():
            cmd_name = command["name"]
            if cmd_name in self._commands:
                logger.warning(f"Command '{cmd_name}' already registered, overriding")
            self._commands[cmd_name] = {
                **command,
                "plugin": plugin_name
            }
        
        # Register event handlers
        for event_name, handler in plugin.get_event_handlers().items():
            self._event_handlers[event_name].append(handler)
        
        # Register prompt providers
        for name, provider in plugin.get_prompt_providers().items():
            if name in self._prompt_providers:
                logger.warning(f"Prompt provider '{name}' already registered, overriding")
            self._prompt_providers[name] = provider
        
        # Register AI adapters
        for name, adapter in plugin.get_ai_adapters().items():
            if name in self._ai_adapters:
                logger.warning(f"AI adapter '{name}' already registered, overriding")
            self._ai_adapters[name] = adapter
        
        # Register output formatters
        for name, formatter in plugin.get_output_formatters().items():
            if name in self._output_formatters:
                logger.warning(f"Output formatter '{name}' already registered, overriding")
            self._output_formatters[name] = formatter
        
        # Register workflow extensions
        for name, workflow in plugin.get_workflow_extensions().items():
            if name in self._workflow_extensions:
                logger.warning(f"Workflow '{name}' already registered, overriding")
            self._workflow_extensions[name] = workflow
        
        # Register storage backends
        for name, backend in plugin.get_storage_backends().items():
            if name in self._storage_backends:
                logger.warning(f"Storage backend '{name}' already registered, overriding")
            self._storage_backends[name] = backend
        
        logger.info(f"Enabled plugin: {plugin_name}")
    
    def disable_plugin(self, plugin_name: str) -> None:
        """Disable a plugin without unregistering it.
        
        Args:
            plugin_name: Name of the plugin to disable
        """
        if plugin_name not in self._plugins:
            raise PluginError(f"Plugin '{plugin_name}' not registered")
        
        plugin = self._plugins[plugin_name]
        
        # Remove commands
        self._commands = {
            name: cmd for name, cmd in self._commands.items()
            if cmd.get("plugin") != plugin_name
        }
        
        # Remove event handlers
        for event_name, handler in plugin.get_event_handlers().items():
            if handler in self._event_handlers[event_name]:
                self._event_handlers[event_name].remove(handler)
        
        # Remove other registrations
        for name in list(self._prompt_providers.keys()):
            if name in plugin.get_prompt_providers():
                del self._prompt_providers[name]
        
        for name in list(self._ai_adapters.keys()):
            if name in plugin.get_ai_adapters():
                del self._ai_adapters[name]
        
        for name in list(self._output_formatters.keys()):
            if name in plugin.get_output_formatters():
                del self._output_formatters[name]
        
        for name in list(self._workflow_extensions.keys()):
            if name in plugin.get_workflow_extensions():
                del self._workflow_extensions[name]
        
        for name in list(self._storage_backends.keys()):
            if name in plugin.get_storage_backends():
                del self._storage_backends[name]
        
        logger.info(f"Disabled plugin: {plugin_name}")
    
    def unregister_plugin(self, plugin_name: str) -> None:
        """Unregister a plugin completely.
        
        Args:
            plugin_name: Name of the plugin to unregister
        """
        if plugin_name not in self._plugins:
            raise PluginError(f"Plugin '{plugin_name}' not registered")
        
        # Disable first
        self.disable_plugin(plugin_name)
        
        # Shutdown the plugin
        plugin = self._plugins[plugin_name]
        try:
            plugin.shutdown()
        except Exception as e:
            logger.error(f"Error shutting down plugin '{plugin_name}': {e}")
        
        # Remove from registry
        del self._plugins[plugin_name]
        
        # Remove from capabilities
        for capability, plugins in self._capabilities.items():
            if plugin_name in plugins:
                plugins.remove(plugin_name)
        
        logger.info(f"Unregistered plugin: {plugin_name}")
    
    def get_plugin(self, plugin_name: str) -> Optional[CruciblePlugin]:
        """Get a registered plugin instance."""
        return self._plugins.get(plugin_name)
    
    def get_plugins_by_capability(
        self,
        capability: PluginCapability
    ) -> List[CruciblePlugin]:
        """Get all plugins that provide a specific capability."""
        plugin_names = self._capabilities.get(capability, [])
        return [
            self._plugins[name] for name in plugin_names
            if name in self._plugins
        ]
    
    def get_command(self, command_name: str) -> Optional[Dict[str, Any]]:
        """Get a registered command."""
        return self._commands.get(command_name)
    
    def get_all_commands(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered commands."""
        return self._commands.copy()
    
    def emit_event(self, event_name: str, payload: Any) -> None:
        """Emit an event to all registered handlers.
        
        Args:
            event_name: Name of the event
            payload: Event payload
        """
        handlers = self._event_handlers.get(event_name, [])
        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                logger.error(f"Error in event handler for '{event_name}': {e}")
    
    def get_prompt_provider(self, name: str) -> Optional[Callable]:
        """Get a prompt provider by name."""
        return self._prompt_providers.get(name)
    
    def get_all_prompt_providers(self) -> Dict[str, Callable]:
        """Get all registered prompt providers."""
        return self._prompt_providers.copy()
    
    def get_ai_adapter(self, name: str) -> Optional[Type]:
        """Get an AI adapter by name."""
        return self._ai_adapters.get(name)
    
    def get_all_ai_adapters(self) -> Dict[str, Type]:
        """Get all registered AI adapters."""
        return self._ai_adapters.copy()
    
    def get_output_formatter(self, name: str) -> Optional[Callable]:
        """Get an output formatter by name."""
        return self._output_formatters.get(name)
    
    def get_all_output_formatters(self) -> Dict[str, Callable]:
        """Get all registered output formatters."""
        return self._output_formatters.copy()
    
    def get_workflow_extension(self, name: str) -> Optional[Callable]:
        """Get a workflow extension by name."""
        return self._workflow_extensions.get(name)
    
    def get_all_workflow_extensions(self) -> Dict[str, Callable]:
        """Get all registered workflow extensions."""
        return self._workflow_extensions.copy()
    
    def get_storage_backend(self, name: str) -> Optional[Type]:
        """Get a storage backend by name."""
        return self._storage_backends.get(name)
    
    def get_all_storage_backends(self) -> Dict[str, Type]:
        """Get all registered storage backends."""
        return self._storage_backends.copy()
    
    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """List all registered plugins with their metadata."""
        result = {}
        for name, plugin in self._plugins.items():
            result[name] = {
                "metadata": plugin.metadata.to_dict(),
                "enabled": name in self._commands or 
                          any(name in self._capabilities[cap] for cap in PluginCapability)
            }
        return result
    
    def shutdown_all(self) -> None:
        """Shutdown all registered plugins."""
        for plugin_name in list(self._plugins.keys()):
            try:
                self.unregister_plugin(plugin_name)
            except Exception as e:
                logger.error(f"Error unregistering plugin '{plugin_name}': {e}")