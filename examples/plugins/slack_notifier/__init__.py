"""Slack notification plugin for Crucible."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict
from pathlib import Path
from datetime import datetime

# Add parent directories to path for imports
import sys
plugin_path = Path(__file__).resolve().parents[3] / "src"
if str(plugin_path) not in sys.path:
    sys.path.append(str(plugin_path))

from crucible.plugins.base import (
    CruciblePlugin,
    PluginMetadata,
    PluginContext,
)


class SlackNotifierPlugin(CruciblePlugin):
    """Plugin for sending notifications to Slack."""
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        manifest_path = Path(__file__).parent / "manifest.json"
        return PluginMetadata.from_manifest(manifest_path)
    
    def initialize(self, context: PluginContext) -> None:
        """Initialize the plugin."""
        self._context = context
        self._webhook_url = context.config.get("webhook_url")
        self._default_channel = context.config.get("default_channel", "#general")
        self._username = context.config.get("username", "Crucible Bot")
        self._initialized = True
    
    def shutdown(self) -> None:
        """Clean up plugin resources."""
        self._initialized = False
    
    def get_event_handlers(self) -> Dict[str, Callable]:
        """Return event handlers."""
        return {
            "idea_created": self._on_idea_created,
            "prompt_generated": self._on_prompt_generated,
            "workflow_completed": self._on_workflow_completed,
        }
    
    def get_output_formatters(self) -> Dict[str, Callable]:
        """Return output formatters."""
        return {
            "slack_message": self._format_slack_message,
            "slack_blocks": self._format_slack_blocks,
        }
    
    def _on_idea_created(self, payload: Dict[str, Any]) -> None:
        """Handle idea_created event."""
        idea = payload.get("idea", {})
        message = {
            "text": f"New idea created: {idea.get('title', 'Untitled')}",
            "channel": self._default_channel,
            "username": self._username,
            "attachments": [
                {
                    "color": "good",
                    "fields": [
                        {
                            "title": "Description",
                            "value": idea.get("description", "No description"),
                            "short": False
                        },
                        {
                            "title": "Created By",
                            "value": idea.get("author", "Unknown"),
                            "short": True
                        },
                        {
                            "title": "Category",
                            "value": idea.get("category", "General"),
                            "short": True
                        }
                    ],
                    "footer": "Crucible",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        self._send_notification(message)
    
    def _on_prompt_generated(self, payload: Dict[str, Any]) -> None:
        """Handle prompt_generated event."""
        prompt_type = payload.get("type", "Unknown")
        topic = payload.get("topic", "Unknown")
        
        message = {
            "text": f"Prompt generated for: {topic}",
            "channel": self._default_channel,
            "username": self._username,
            "attachments": [
                {
                    "color": "3AA3E3",
                    "fields": [
                        {
                            "title": "Prompt Type",
                            "value": prompt_type,
                            "short": True
                        },
                        {
                            "title": "Topic",
                            "value": topic,
                            "short": True
                        }
                    ]
                }
            ]
        }
        self._send_notification(message)
    
    def _on_workflow_completed(self, payload: Dict[str, Any]) -> None:
        """Handle workflow_completed event."""
        workflow = payload.get("workflow", "Unknown")
        status = payload.get("status", "Unknown")
        duration = payload.get("duration", 0)
        
        color = "good" if status == "success" else "danger"
        
        message = {
            "text": f"Workflow '{workflow}' completed",
            "channel": self._default_channel,
            "username": self._username,
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": "Status",
                            "value": status.capitalize(),
                            "short": True
                        },
                        {
                            "title": "Duration",
                            "value": f"{duration:.2f} seconds",
                            "short": True
                        }
                    ]
                }
            ]
        }
        self._send_notification(message)
    
    def _format_slack_message(self, content: Dict[str, Any]) -> str:
        """Format content as a Slack message."""
        # Extract key information
        title = content.get("title", "Crucible Update")
        body = content.get("body", "")
        fields = content.get("fields", {})
        
        # Build message
        message = f"*{title}*\n\n{body}\n"
        
        if fields:
            for key, value in fields.items():
                message += f"\n*{key}:* {value}"
        
        return json.dumps({
            "text": message,
            "channel": self._default_channel,
            "username": self._username
        })
    
    def _format_slack_blocks(self, content: Dict[str, Any]) -> str:
        """Format content as Slack blocks."""
        blocks = []
        
        # Header block
        if "title" in content:
            blocks.append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": content["title"]
                }
            })
        
        # Section blocks
        if "sections" in content:
            for section in content["sections"]:
                block = {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": section.get("text", "")
                    }
                }
                
                if "fields" in section:
                    block["fields"] = [
                        {
                            "type": "mrkdwn",
                            "text": f"*{field['title']}*\n{field['value']}"
                        }
                        for field in section["fields"]
                    ]
                
                blocks.append(block)
        
        # Action blocks
        if "actions" in content:
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": action["text"]
                        },
                        "url": action.get("url"),
                        "value": action.get("value"),
                        "style": action.get("style", "primary")
                    }
                    for action in content["actions"]
                ]
            })
        
        return json.dumps({
            "blocks": blocks,
            "channel": self._default_channel,
            "username": self._username
        })
    
    def _send_notification(self, message: Dict[str, Any]) -> None:
        """Send a notification to Slack."""
        # In a real implementation, this would make an HTTP POST request
        # to the webhook URL. For demo purposes, we just log it.
        print(f"[Slack Notifier] Would send to {self._webhook_url}:")
        print(json.dumps(message, indent=2))