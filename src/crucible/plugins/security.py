"""Security features for the plugin system."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import logging

from .base import PluginError, PluginValidationError


logger = logging.getLogger(__name__)


class PluginSecurityManager:
    """Manages security aspects of plugins."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the security manager.
        
        Args:
            config: Security configuration
        """
        self.config = config or {}
        self._trusted_plugins: Set[str] = set(self.config.get("trusted_plugins", []))
        self._blocked_plugins: Set[str] = set(self.config.get("blocked_plugins", []))
        self._allowed_capabilities: Set[str] = set(
            self.config.get("allowed_capabilities", [cap.value for cap in PluginCapability])
        )
        self._sandbox_enabled = self.config.get("sandbox_enabled", True)
        self._signature_verification = self.config.get("signature_verification", False)
    
    def validate_plugin_security(
        self,
        plugin_name: str,
        plugin_path: Path,
        metadata: Dict[str, Any]
    ) -> None:
        """Validate plugin security before loading.
        
        Args:
            plugin_name: Name of the plugin
            plugin_path: Path to the plugin directory
            metadata: Plugin metadata
            
        Raises:
            PluginValidationError: If plugin fails security validation
        """
        # Check if plugin is blocked
        if plugin_name in self._blocked_plugins:
            raise PluginValidationError(f"Plugin '{plugin_name}' is blocked")
        
        # Validate capabilities
        capabilities = metadata.get("capabilities", [])
        for capability in capabilities:
            if capability not in self._allowed_capabilities:
                raise PluginValidationError(
                    f"Plugin '{plugin_name}' requests disallowed capability: {capability}"
                )
        
        # Check file permissions
        self._check_file_permissions(plugin_path)
        
        # Verify plugin signature if enabled
        if self._signature_verification and plugin_name not in self._trusted_plugins:
            self._verify_plugin_signature(plugin_path, metadata)
        
        # Scan for suspicious patterns
        self._scan_plugin_code(plugin_path)
    
    def get_plugin_sandbox_config(self, plugin_name: str) -> Dict[str, Any]:
        """Get sandbox configuration for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Sandbox configuration
        """
        if not self._sandbox_enabled or plugin_name in self._trusted_plugins:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "restrictions": {
                "network_access": False,
                "file_system_access": "restricted",  # Only plugin data dir
                "subprocess_access": False,
                "import_restrictions": [
                    "os",
                    "subprocess",
                    "socket",
                    "__builtins__"
                ]
            }
        }
    
    def _check_file_permissions(self, plugin_path: Path) -> None:
        """Check file permissions for security issues."""
        # Check that plugin files are not world-writable
        for file_path in plugin_path.rglob("*"):
            if file_path.is_file():
                mode = file_path.stat().st_mode
                if mode & 0o002:  # World writable
                    logger.warning(
                        f"Plugin file {file_path} is world-writable, "
                        "this is a security risk"
                    )
    
    def _verify_plugin_signature(
        self,
        plugin_path: Path,
        metadata: Dict[str, Any]
    ) -> None:
        """Verify plugin signature.
        
        Args:
            plugin_path: Path to plugin directory
            metadata: Plugin metadata
            
        Raises:
            PluginValidationError: If signature verification fails
        """
        signature_file = plugin_path / "plugin.sig"
        if not signature_file.exists():
            raise PluginValidationError(
                "Plugin signature file not found. "
                "Unsigned plugins must be explicitly trusted."
            )
        
        # In a real implementation, this would verify a cryptographic signature
        # For demo purposes, we just check a simple hash
        expected_hash = metadata.get("content_hash")
        if not expected_hash:
            raise PluginValidationError("Plugin metadata missing content hash")
        
        actual_hash = self._calculate_plugin_hash(plugin_path)
        if actual_hash != expected_hash:
            raise PluginValidationError("Plugin signature verification failed")
    
    def _calculate_plugin_hash(self, plugin_path: Path) -> str:
        """Calculate hash of plugin files."""
        hasher = hashlib.sha256()
        
        # Hash all Python files in the plugin
        for py_file in sorted(plugin_path.glob("*.py")):
            with open(py_file, 'rb') as f:
                hasher.update(f.read())
        
        return hasher.hexdigest()
    
    def _scan_plugin_code(self, plugin_path: Path) -> None:
        """Scan plugin code for suspicious patterns."""
        suspicious_patterns = [
            "eval(",
            "exec(",
            "__import__",
            "compile(",
            "globals()",
            "locals()",
            "setattr(",
            "delattr(",
            "__dict__",
            "__builtins__",
        ]
        
        for py_file in plugin_path.glob("*.py"):
            with open(py_file) as f:
                content = f.read()
            
            for pattern in suspicious_patterns:
                if pattern in content:
                    logger.warning(
                        f"Suspicious pattern '{pattern}' found in {py_file}. "
                        "This plugin may require additional review."
                    )
    
    def add_trusted_plugin(self, plugin_name: str) -> None:
        """Add a plugin to the trusted list."""
        self._trusted_plugins.add(plugin_name)
        if plugin_name in self._blocked_plugins:
            self._blocked_plugins.remove(plugin_name)
    
    def add_blocked_plugin(self, plugin_name: str) -> None:
        """Add a plugin to the blocked list."""
        self._blocked_plugins.add(plugin_name)
        if plugin_name in self._trusted_plugins:
            self._trusted_plugins.remove(plugin_name)
    
    def is_plugin_trusted(self, plugin_name: str) -> bool:
        """Check if a plugin is trusted."""
        return plugin_name in self._trusted_plugins
    
    def is_plugin_blocked(self, plugin_name: str) -> bool:
        """Check if a plugin is blocked."""
        return plugin_name in self._blocked_plugins
    
    def get_security_report(self) -> Dict[str, Any]:
        """Get a security report of the plugin system."""
        return {
            "sandbox_enabled": self._sandbox_enabled,
            "signature_verification": self._signature_verification,
            "trusted_plugins": list(self._trusted_plugins),
            "blocked_plugins": list(self._blocked_plugins),
            "allowed_capabilities": list(self._allowed_capabilities)
        }


# Import at end to avoid circular dependency
from .base import PluginCapability