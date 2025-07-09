import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from cli import (
    list_blueprints_formatted, format_output, write_output, 
    blueprint_by_name, brainstorm_command, prompt_generate_command,
    main
)


class TestBlueprintFiltering:
    def test_list_blueprints_no_filter(self):
        blueprints = list_blueprints_formatted()
        assert len(blueprints) > 0
        assert all(isinstance(bp, tuple) and len(bp) == 2 for bp in blueprints)
    
    def test_list_blueprints_search(self):
        # Search by name
        results = list_blueprints_formatted(search="domain")
        assert len(results) > 0
        assert all("domain" in name.lower() or "domain" in desc.lower() 
                  for name, desc in results)
        
        # Search that should return no results
        results = list_blueprints_formatted(search="xyznonexistent")
        assert len(results) == 0
    
    def test_list_blueprints_category(self):
        # Filter by category (filename pattern)
        results = list_blueprints_formatted(category="001")
        assert len(results) > 0
        assert all("001" in name.lower() for name, desc in results)


class TestOutputFormatting:
    def test_format_output_text(self):
        content = "Test content"
        result = format_output(content, "text")
        assert result == content
    
    def test_format_output_json(self):
        content = "Test content"
        result = format_output(content, "json")
        parsed = json.loads(result)
        assert parsed["content"] == content
    
    def test_format_output_yaml(self):
        # Test only if yaml is available
        try:
            import yaml
            content = "Test content"
            result = format_output(content, "yaml")
            assert "content: Test content" in result
        except ImportError:
            pytest.skip("PyYAML not installed")
    
    def test_write_output_stdout(self, capsys):
        content = "Test output"
        write_output(content)
        captured = capsys.readouterr()
        assert content in captured.out
    
    def test_write_output_file(self, tmp_path):
        content = "Test file output"
        output_file = tmp_path / "test_output.txt"
        write_output(content, str(output_file))
        
        assert output_file.exists()
        assert output_file.read_text() == content


class TestBlueprintByName:
    def test_blueprint_exact_match(self, monkeypatch, capsys):
        # Mock copy_blueprint
        copied = []
        monkeypatch.setattr("cli.copy_blueprint", lambda name: copied.append(name))
        
        # Use a known blueprint
        blueprint_by_name("001_domain_expert_persona.md")
        
        assert len(copied) == 1
        assert copied[0] == "001_domain_expert_persona.md"
        
        captured = capsys.readouterr()
        assert "Copied" in captured.out
    
    def test_blueprint_partial_match(self, monkeypatch, capsys):
        copied = []
        monkeypatch.setattr("cli.copy_blueprint", lambda name: copied.append(name))
        
        # Partial match should work if unique
        blueprint_by_name("domain_expert")
        
        assert len(copied) == 1
        assert "domain_expert" in copied[0]
    
    def test_blueprint_multiple_matches(self, capsys):
        # Search that will match multiple blueprints
        blueprint_by_name("0")  # Should match multiple numbered blueprints
        
        captured = capsys.readouterr()
        assert "Multiple blueprints match" in captured.out
    
    def test_blueprint_no_match(self, capsys):
        blueprint_by_name("xyznonexistent")
        
        captured = capsys.readouterr()
        assert "No blueprint found" in captured.out
    
    def test_blueprint_to_file(self, tmp_path):
        output_file = tmp_path / "blueprint.txt"
        blueprint_by_name("001_domain_expert_persona.md", output_file=str(output_file))
        
        assert output_file.exists()
        content = output_file.read_text()
        assert len(content) > 0


class TestBrainstormCommand:
    def test_brainstorm_basic(self, capsys):
        brainstorm_command("test topic")
        
        captured = capsys.readouterr()
        assert len(captured.out) > 0
    
    def test_brainstorm_to_file(self, tmp_path):
        output_file = tmp_path / "brainstorm.txt"
        brainstorm_command("test topic", output_file=str(output_file))
        
        assert output_file.exists()
        content = output_file.read_text()
        assert len(content) > 0
    
    def test_brainstorm_json_format(self, tmp_path):
        output_file = tmp_path / "brainstorm.json"
        brainstorm_command("test topic", output_format="json", output_file=str(output_file))
        
        assert output_file.exists()
        content = output_file.read_text()
        parsed = json.loads(content)
        assert "content" in parsed


class TestPromptGenerateCommand:
    def test_prompt_generate_basic(self, capsys):
        prompt_generate_command("test context")
        
        captured = capsys.readouterr()
        # Should generate a prompt (length check instead of content check)
        assert len(captured.out) > 0
        # Could include AI usage info
        assert "AI Usage" in captured.out or len(captured.out) > 50
    
    def test_prompt_generate_to_file(self, tmp_path):
        output_file = tmp_path / "prompt.txt"
        prompt_generate_command("test context", output_file=str(output_file))
        
        assert output_file.exists()
        content = output_file.read_text()
        # Should have generated prompt content
        assert len(content) > 0


class TestCLIIntegration:
    def test_blueprint_list_command(self, capsys):
        main(["blueprint", "--list"])
        
        captured = capsys.readouterr()
        assert "Available blueprints:" in captured.out
        assert ".md" in captured.out
    
    def test_blueprint_search_command(self, capsys):
        main(["blueprint", "--list", "--search", "domain"])
        
        captured = capsys.readouterr()
        assert "Available blueprints:" in captured.out or "No blueprints found" in captured.out
    
    def test_blueprint_name_command(self, monkeypatch, capsys):
        copied = []
        monkeypatch.setattr("cli.copy_blueprint", lambda name: copied.append(name))
        
        main(["blueprint", "--name", "domain_expert"])
        
        assert len(copied) == 1
    
    def test_brainstorm_command_cli(self, capsys):
        main(["brainstorm", "innovative ideas"])
        
        captured = capsys.readouterr()
        assert len(captured.out) > 0
    
    def test_prompt_generate_command_cli(self, capsys):
        main(["prompt", "generate", "API design patterns"])
        
        captured = capsys.readouterr()
        # Should generate a prompt
        assert len(captured.out) > 0
        # Check for AI usage or reasonable prompt content
        assert "AI Usage" in captured.out or len(captured.out) > 50
    
    def test_help_message(self, capsys):
        with pytest.raises(SystemExit):
            main(["--help"])
        
        captured = capsys.readouterr()
        assert "Crucible CLI" in captured.out
        assert "Examples:" in captured.out
    
    def test_blueprint_help(self, capsys):
        with pytest.raises(SystemExit):
            main(["blueprint", "--help"])
        
        captured = capsys.readouterr()
        assert "blueprint" in captured.out
        assert "--list" in captured.out
        assert "--search" in captured.out
    
    def test_invalid_command(self, capsys):
        # Invalid command should exit with error
        with pytest.raises(SystemExit):
            main(["invalid_command"])
        
        captured = capsys.readouterr()
        assert "invalid choice" in captured.err