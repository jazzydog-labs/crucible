"""Crucible Plugin System.

This module provides a formal plugin system for extending Crucible's functionality.
Plugins can add custom prompt providers, AI adapters, output formatters, workflows,
and storage backends.
"""

from __future__ import annotations

from .base import (
    CruciblePlugin,
    PluginMetadata,
    PluginCapability,
    PluginContext,
    PluginError,
    PluginLoadError,
    PluginValidationError,
)
from .loader import PluginLoader
from .registry import PluginRegistry

__all__ = [
    "CruciblePlugin",
    "PluginMetadata",
    "PluginCapability",
    "PluginContext",
    "PluginError",
    "PluginLoadError",
    "PluginValidationError",
    "PluginLoader",
    "PluginRegistry",
]