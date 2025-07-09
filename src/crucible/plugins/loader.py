"""Plugin loader for discovering and loading Crucible plugins."""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type
import json
import logging

from .base import (
    CruciblePlugin,
    PluginMetadata,
    PluginContext,
    PluginLoadError,
    PluginValidationError,
)


logger = logging.getLogger(__name__)


class PluginLoader:
    """Loads and manages Crucible plugins."""
    
    def __init__(self, plugin_dirs: Optional[List[Path]] = None) -> None:
        """Initialize the plugin loader.
        
        Args:
            plugin_dirs: Directories to search for plugins
        """
        self.plugin_dirs = plugin_dirs or self._default_plugin_dirs()
        self._loaded_plugins: Dict[str, Type[CruciblePlugin]] = {}
        self._plugin_metadata: Dict[str, PluginMetadata] = {}
    
    def _default_plugin_dirs(self) -> List[Path]:
        """Get default plugin directories."""
        dirs = []
        
        # User plugins directory
        user_dir = Path.home() / ".crucible" / "plugins"
        if user_dir.exists():
            dirs.append(user_dir)
        
        # System plugins directory (if installed)
        try:
            import crucible
            package_dir = Path(crucible.__file__).parent / "plugins" / "builtin"
            if package_dir.exists():
                dirs.append(package_dir)
        except ImportError:
            pass
        
        # Current directory plugins
        current_dir = Path.cwd() / "plugins"
        if current_dir.exists():
            dirs.append(current_dir)
        
        return dirs
    
    def discover_plugins(self) -> Dict[str, PluginMetadata]:
        """Discover all available plugins.
        
        Returns:
            Dictionary mapping plugin names to metadata
        """
        discovered = {}
        
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
            
            # Look for plugin directories with manifest.json
            for item in plugin_dir.iterdir():
                if item.is_dir():
                    manifest_path = item / "manifest.json"
                    if manifest_path.exists():
                        try:
                            metadata = PluginMetadata.from_manifest(manifest_path)
                            discovered[metadata.name] = metadata
                            logger.info(f"Discovered plugin: {metadata.name} v{metadata.version}")
                        except Exception as e:
                            logger.error(f"Failed to load manifest from {manifest_path}: {e}")
        
        return discovered
    
    def load_plugin(self, plugin_name: str) -> Type[CruciblePlugin]:
        """Load a specific plugin.
        
        Args:
            plugin_name: Name of the plugin to load
            
        Returns:
            Plugin class
            
        Raises:
            PluginLoadError: If plugin cannot be loaded
        """
        if plugin_name in self._loaded_plugins:
            return self._loaded_plugins[plugin_name]
        
        # Find plugin directory
        plugin_dir = self._find_plugin_dir(plugin_name)
        if not plugin_dir:
            raise PluginLoadError(f"Plugin '{plugin_name}' not found")
        
        # Load manifest
        manifest_path = plugin_dir / "manifest.json"
        if not manifest_path.exists():
            raise PluginLoadError(f"No manifest.json found for plugin '{plugin_name}'")
        
        try:
            metadata = PluginMetadata.from_manifest(manifest_path)
        except Exception as e:
            raise PluginLoadError(f"Invalid manifest for plugin '{plugin_name}': {e}")
        
        # Load plugin module
        plugin_module_path = plugin_dir / "__init__.py"
        if not plugin_module_path.exists():
            plugin_module_path = plugin_dir / f"{plugin_name}.py"
        
        if not plugin_module_path.exists():
            raise PluginLoadError(
                f"No __init__.py or {plugin_name}.py found for plugin '{plugin_name}'"
            )
        
        # Import the module
        try:
            module = self._import_plugin_module(plugin_name, plugin_module_path)
        except Exception as e:
            raise PluginLoadError(f"Failed to import plugin '{plugin_name}': {e}")
        
        # Find plugin class
        plugin_class = self._find_plugin_class(module, metadata)
        if not plugin_class:
            raise PluginLoadError(
                f"No CruciblePlugin subclass found in plugin '{plugin_name}'"
            )
        
        # Validate plugin
        self._validate_plugin_class(plugin_class, metadata)
        
        # Cache the plugin
        self._loaded_plugins[plugin_name] = plugin_class
        self._plugin_metadata[plugin_name] = metadata
        
        logger.info(f"Loaded plugin: {plugin_name} v{metadata.version}")
        return plugin_class
    
    def load_all_plugins(self) -> Dict[str, Type[CruciblePlugin]]:
        """Load all discovered plugins.
        
        Returns:
            Dictionary mapping plugin names to plugin classes
        """
        discovered = self.discover_plugins()
        loaded = {}
        
        for plugin_name in discovered:
            try:
                plugin_class = self.load_plugin(plugin_name)
                loaded[plugin_name] = plugin_class
            except PluginLoadError as e:
                logger.error(f"Failed to load plugin '{plugin_name}': {e}")
        
        return loaded
    
    def create_plugin_instance(
        self,
        plugin_name: str,
        context: PluginContext
    ) -> CruciblePlugin:
        """Create an instance of a plugin.
        
        Args:
            plugin_name: Name of the plugin
            context: Plugin context
            
        Returns:
            Initialized plugin instance
        """
        plugin_class = self.load_plugin(plugin_name)
        
        # Create instance
        try:
            plugin = plugin_class()
        except Exception as e:
            raise PluginLoadError(f"Failed to instantiate plugin '{plugin_name}': {e}")
        
        # Validate configuration
        try:
            plugin.validate_config(context.config)
        except PluginValidationError as e:
            raise PluginLoadError(f"Invalid configuration for plugin '{plugin_name}': {e}")
        
        # Initialize plugin
        try:
            plugin.initialize(context)
        except Exception as e:
            raise PluginLoadError(f"Failed to initialize plugin '{plugin_name}': {e}")
        
        return plugin
    
    def _find_plugin_dir(self, plugin_name: str) -> Optional[Path]:
        """Find the directory containing a plugin."""
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
            
            candidate = plugin_dir / plugin_name
            if candidate.is_dir() and (candidate / "manifest.json").exists():
                return candidate
        
        return None
    
    def _import_plugin_module(self, plugin_name: str, module_path: Path):
        """Import a plugin module."""
        spec = importlib.util.spec_from_file_location(
            f"crucible_plugin_{plugin_name}",
            module_path
        )
        
        if not spec or not spec.loader:
            raise ImportError(f"Could not load spec for {module_path}")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        
        return module
    
    def _find_plugin_class(
        self,
        module,
        metadata: PluginMetadata
    ) -> Optional[Type[CruciblePlugin]]:
        """Find the plugin class in a module."""
        # Look for a class with the plugin name
        expected_class_name = "".join(word.capitalize() for word in metadata.name.split("_"))
        
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, CruciblePlugin) and 
                obj is not CruciblePlugin):
                # Prefer class matching expected name
                if name == expected_class_name or name == f"{expected_class_name}Plugin":
                    return obj
        
        # If no exact match, return first CruciblePlugin subclass
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, CruciblePlugin) and 
                obj is not CruciblePlugin):
                return obj
        
        return None
    
    def _validate_plugin_class(
        self,
        plugin_class: Type[CruciblePlugin],
        metadata: PluginMetadata
    ) -> None:
        """Validate that a plugin class implements required methods."""
        # Check that metadata property returns the expected metadata
        try:
            instance = plugin_class()
            plugin_metadata = instance.metadata
            
            # Basic validation
            if plugin_metadata.name != metadata.name:
                raise PluginValidationError(
                    f"Plugin metadata name '{plugin_metadata.name}' does not match "
                    f"manifest name '{metadata.name}'"
                )
        except Exception as e:
            raise PluginValidationError(f"Failed to validate plugin class: {e}")
    
    def get_plugin_metadata(self, plugin_name: str) -> Optional[PluginMetadata]:
        """Get metadata for a loaded plugin."""
        return self._plugin_metadata.get(plugin_name)