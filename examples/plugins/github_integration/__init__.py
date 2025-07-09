"""GitHub integration plugin for Crucible."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List
from pathlib import Path

# Add parent directories to path for imports
import sys
sys.path.append(str(Path(__file__).resolve().parents[4]))

from src.crucible.plugins.base import (
    CruciblePlugin,
    PluginMetadata,
    PluginContext,
)


class GitHubIntegrationPlugin(CruciblePlugin):
    """Plugin for integrating with GitHub."""
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        manifest_path = Path(__file__).parent / "manifest.json"
        return PluginMetadata.from_manifest(manifest_path)
    
    def initialize(self, context: PluginContext) -> None:
        """Initialize the plugin."""
        self._context = context
        self._token = context.config.get("token")
        self._default_repo = context.config.get("default_repo")
        self._initialized = True
        
        # Get plugin data directory
        self._data_dir = context.get_plugin_data_dir("github_integration")
        
        # Load cached data if exists
        self._cache_file = self._data_dir / "cache.json"
        self._cache = self._load_cache()
    
    def shutdown(self) -> None:
        """Clean up plugin resources."""
        # Save cache
        self._save_cache()
        self._initialized = False
    
    def get_commands(self) -> List[Dict[str, Any]]:
        """Return CLI commands provided by this plugin."""
        return [
            {
                "name": "gh-issues",
                "description": "List GitHub issues",
                "handler": self._list_issues_command,
                "args": [
                    {
                        "name": "repo",
                        "type": "str",
                        "help": "Repository (owner/repo)",
                        "required": False
                    },
                    {
                        "name": "--state",
                        "type": "str",
                        "help": "Issue state (open, closed, all)",
                        "default": "open"
                    }
                ]
            },
            {
                "name": "gh-create-issue",
                "description": "Create a GitHub issue from an idea",
                "handler": self._create_issue_command,
                "args": [
                    {
                        "name": "title",
                        "type": "str",
                        "help": "Issue title"
                    },
                    {
                        "name": "--body",
                        "type": "str",
                        "help": "Issue body",
                        "required": False
                    },
                    {
                        "name": "--repo",
                        "type": "str",
                        "help": "Repository (owner/repo)",
                        "required": False
                    }
                ]
            }
        ]
    
    def get_prompt_providers(self) -> Dict[str, Callable]:
        """Return prompt providers."""
        return {
            "github_issue_template": self._provide_issue_template,
            "github_pr_template": self._provide_pr_template,
        }
    
    def get_workflow_extensions(self) -> Dict[str, Callable]:
        """Return workflow extensions."""
        return {
            "idea_to_issue": self._idea_to_issue_workflow,
            "generate_pr_description": self._generate_pr_description_workflow,
        }
    
    def _list_issues_command(self, repo: str = None, state: str = "open") -> str:
        """List GitHub issues command handler."""
        repo = repo or self._default_repo
        if not repo:
            return "Error: No repository specified and no default repo configured"
        
        # In a real implementation, this would use the GitHub API
        # For demo purposes, return mock data
        return f"Listing {state} issues for {repo}:\n" \
               f"- #123: Implement new feature\n" \
               f"- #124: Fix bug in parser\n" \
               f"- #125: Update documentation"
    
    def _create_issue_command(self, title: str, body: str = None, repo: str = None) -> str:
        """Create GitHub issue command handler."""
        repo = repo or self._default_repo
        if not repo:
            return "Error: No repository specified and no default repo configured"
        
        # In a real implementation, this would use the GitHub API
        # For demo purposes, return success message
        issue_number = 126  # Mock issue number
        return f"Created issue #{issue_number} in {repo}: {title}"
    
    def _provide_issue_template(self, context: Dict[str, Any]) -> str:
        """Provide GitHub issue template."""
        title = context.get("title", "New Issue")
        description = context.get("description", "")
        
        template = f"""## {title}

### Description
{description}

### Steps to Reproduce
1. 
2. 
3. 

### Expected Behavior


### Actual Behavior


### Environment
- OS: 
- Version: 
- Browser (if applicable): 
"""
        return template
    
    def _provide_pr_template(self, context: Dict[str, Any]) -> str:
        """Provide GitHub PR template."""
        title = context.get("title", "New Feature/Fix")
        description = context.get("description", "")
        issue = context.get("issue", "")
        
        template = f"""## {title}

### Description
{description}

### Related Issue
{f"Fixes #{issue}" if issue else "N/A"}

### Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

### Checklist
- [ ] My code follows the project style guidelines
- [ ] I have performed a self-review
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing tests pass locally
- [ ] I have updated the documentation accordingly
"""
        return template
    
    def _idea_to_issue_workflow(self, idea: str, repo: str = None) -> Dict[str, Any]:
        """Convert an idea to a GitHub issue."""
        repo = repo or self._default_repo
        
        # In a real implementation, this would:
        # 1. Use AI to expand the idea
        # 2. Create a properly formatted issue
        # 3. Submit to GitHub API
        
        return {
            "status": "success",
            "issue": {
                "number": 127,
                "title": f"Idea: {idea[:50]}...",
                "body": f"This issue was generated from the idea:\n\n{idea}",
                "url": f"https://github.com/{repo}/issues/127"
            }
        }
    
    def _generate_pr_description_workflow(self, changes: List[str], issue: str = None) -> str:
        """Generate a PR description from a list of changes."""
        # In a real implementation, this would use AI to generate
        # a comprehensive PR description
        
        description = "## Summary\n\n"
        description += "This PR includes the following changes:\n\n"
        for change in changes:
            description += f"- {change}\n"
        
        if issue:
            description += f"\n## Related Issue\nFixes #{issue}\n"
        
        return description
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cached data."""
        if self._cache_file.exists():
            with open(self._cache_file) as f:
                return json.load(f)
        return {}
    
    def _save_cache(self) -> None:
        """Save cache data."""
        with open(self._cache_file, 'w') as f:
            json.dump(self._cache, f, indent=2)