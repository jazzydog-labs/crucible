"""Base classes and interfaces for the Crucible plugin system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type
import json
from pathlib import Path


class PluginCapability(Enum):
    """Capabilities that plugins can provide."""
    
    PROMPT_PROVIDER = "prompt_provider"
    AI_ADAPTER = "ai_adapter"
    OUTPUT_FORMATTER = "output_formatter"
    WORKFLOW_EXTENSION = "workflow_extension"
    STORAGE_BACKEND = "storage_backend"
    EVENT_HANDLER = "event_handler"
    CLI_COMMAND = "cli_command"
    INTEGRATION = "integration"  # External service integrations (GitHub, Slack, etc.)


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    
    name: str
    version: str
    description: str
    author: str
    capabilities: List[PluginCapability]
    dependencies: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_manifest(cls, manifest_path: Path) -> PluginMetadata:
        """Load metadata from a manifest file."""
        with open(manifest_path) as f:
            data = json.load(f)
        
        # Convert capability strings to enums
        capabilities = [
            PluginCapability(cap) for cap in data.get("capabilities", [])
        ]
        
        return cls(
            name=data["name"],
            version=data["version"],
            description=data["description"],
            author=data["author"],
            capabilities=capabilities,
            dependencies=data.get("dependencies", []),
            config_schema=data.get("config_schema"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "capabilities": [cap.value for cap in self.capabilities],
            "dependencies": self.dependencies,
            "config_schema": self.config_schema,
        }


@dataclass
class PluginContext:
    """Context provided to plugins during initialization."""
    
    config: Dict[str, Any]
    event_bus: Optional[Any] = None  # Avoid circular import
    ai_model: Optional[Any] = None
    data_dir: Optional[Path] = None
    
    def get_plugin_data_dir(self, plugin_name: str) -> Path:
        """Get a data directory for the plugin."""
        if not self.data_dir:
            self.data_dir = Path.home() / ".crucible" / "plugins"
        
        plugin_dir = self.data_dir / plugin_name
        plugin_dir.mkdir(parents=True, exist_ok=True)
        return plugin_dir


class CruciblePlugin(ABC):
    """Base class for all Crucible plugins."""
    
    def __init__(self) -> None:
        self._metadata: Optional[PluginMetadata] = None
        self._context: Optional[PluginContext] = None
        self._initialized = False
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @abstractmethod
    def initialize(self, context: PluginContext) -> None:
        """Initialize the plugin with the given context.
        
        Args:
            context: Plugin context with configuration and resources
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Clean up plugin resources."""
        pass
    
    def get_commands(self) -> List[Dict[str, Any]]:
        """Return CLI commands provided by this plugin.
        
        Returns:
            List of command definitions, each with:
            - name: Command name
            - description: Command description
            - handler: Callable that handles the command
            - args: List of argument definitions
        """
        return []
    
    def get_event_handlers(self) -> Dict[str, Callable]:
        """Return event handlers provided by this plugin.
        
        Returns:
            Dictionary mapping event names to handler functions
        """
        return {}
    
    def get_prompt_providers(self) -> Dict[str, Callable]:
        """Return prompt providers for custom blueprint sources.
        
        Returns:
            Dictionary mapping provider names to functions that return prompts
        """
        return {}
    
    def get_ai_adapters(self) -> Dict[str, Type]:
        """Return AI adapter classes for different AI services.
        
        Returns:
            Dictionary mapping adapter names to adapter classes
        """
        return {}
    
    def get_output_formatters(self) -> Dict[str, Callable]:
        """Return output formatters for custom export formats.
        
        Returns:
            Dictionary mapping format names to formatter functions
        """
        return {}
    
    def get_workflow_extensions(self) -> Dict[str, Callable]:
        """Return workflow extensions for complex processes.
        
        Returns:
            Dictionary mapping workflow names to workflow functions
        """
        return {}
    
    def get_storage_backends(self) -> Dict[str, Type]:
        """Return storage backend classes.
        
        Returns:
            Dictionary mapping backend names to backend classes
        """
        return {}
    
    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate plugin configuration.
        
        Args:
            config: Configuration to validate
            
        Raises:
            PluginValidationError: If configuration is invalid
        """
        if not self.metadata.config_schema:
            return
        
        # Basic schema validation
        # In a real implementation, we'd use jsonschema
        required_keys = self.metadata.config_schema.get("required", [])
        for key in required_keys:
            if key not in config:
                raise PluginValidationError(
                    f"Missing required configuration key: {key}"
                )


class PluginError(Exception):
    """Base exception for plugin errors."""
    pass


class PluginLoadError(PluginError):
    """Error loading a plugin."""
    pass


class PluginValidationError(PluginError):
    """Error validating plugin configuration or metadata."""
    pass