# Crucible Plugin Examples

This directory contains example plugins demonstrating how to extend Crucible's functionality.

## Plugin Structure

Each plugin should have:
- `manifest.json` - Plugin metadata and configuration
- `__init__.py` or `<plugin_name>.py` - Plugin implementation
- `README.md` - Plugin documentation

## Example Plugins

1. **github_integration** - Integrates with GitHub API for issue/PR management
2. **slack_notifier** - Sends notifications to Slack channels
3. **custom_ai_provider** - Adds support for alternative AI providers

## Manifest Format

```json
{
    "name": "plugin_name",
    "version": "1.0.0",
    "description": "Plugin description",
    "author": "Author Name",
    "capabilities": ["prompt_provider", "workflow_extension"],
    "dependencies": ["requests>=2.28.0"],
    "config_schema": {
        "type": "object",
        "properties": {
            "api_key": {"type": "string"},
            "endpoint": {"type": "string"}
        },
        "required": ["api_key"]
    }
}
```

## Creating a Plugin

1. Create a new directory with your plugin name
2. Add a manifest.json file
3. Implement your plugin class extending `CruciblePlugin`
4. Place in `~/.crucible/plugins/` or specify custom path