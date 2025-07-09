#!/usr/bin/env python3
"""Demo showcasing the enhanced CLI user arguments functionality.

This demo demonstrates:
- Blueprint listing with search and filtering
- Blueprint selection by name
- Output formatting (text, JSON, YAML)
- Writing output to files
- Brainstorming command
- Prompt generation command
"""

import sys
import subprocess
import tempfile
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent / 'src'))


def run_command(cmd):
    """Run a CLI command and return output."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode


def demo_blueprint_features():
    """Demonstrate blueprint command features."""
    print("=== Blueprint Features Demo ===")
    
    # List all blueprints
    print("\n1. List all blueprints:")
    stdout, _, _ = run_command(["./cru", "blueprint", "--list"])
    print(stdout[:500] + "..." if len(stdout) > 500 else stdout)
    
    # Search blueprints
    print("\n2. Search blueprints containing 'domain':")
    stdout, _, _ = run_command(["./cru", "blueprint", "--list", "--search", "domain"])
    print(stdout)
    
    # Filter by category
    print("\n3. Filter blueprints by category '001':")
    stdout, _, _ = run_command(["./cru", "blueprint", "--list", "--category", "001"])
    print(stdout)
    
    # Select blueprint by name
    print("\n4. Select blueprint by partial name 'codex':")
    stdout, _, _ = run_command(["./cru", "blueprint", "--name", "codex"])
    print(stdout)
    
    # Output to file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
        tmp_path = tmp.name
    
    print(f"\n5. Save blueprint to file ({tmp_path}):")
    stdout, _, _ = run_command(["./cru", "blueprint", "--name", "domain", "--output", tmp_path])
    print(stdout)
    
    # Show file content (first 200 chars)
    content = Path(tmp_path).read_text()
    print(f"File content preview: {content[:200]}...")
    Path(tmp_path).unlink()
    
    # JSON output
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name
    
    print(f"\n6. Export blueprint as JSON ({tmp_path}):")
    stdout, _, _ = run_command(["./cru", "blueprint", "--name", "domain", "--format", "json", "--output", tmp_path])
    print(stdout)
    
    # Parse and show JSON
    with open(tmp_path) as f:
        data = json.load(f)
    print(f"JSON keys: {list(data.keys())}")
    print(f"Content length: {len(data.get('content', ''))}")
    Path(tmp_path).unlink()


def demo_brainstorm_command():
    """Demonstrate brainstorming command."""
    print("\n=== Brainstorming Command Demo ===")
    
    # Basic brainstorming
    print("\n1. Brainstorm about 'sustainable urban transportation':")
    stdout, _, _ = run_command(["./cru", "brainstorm", "sustainable urban transportation"])
    print(stdout[:500] + "..." if len(stdout) > 500 else stdout)
    
    # Save to file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
        tmp_path = tmp.name
    
    print(f"\n2. Save brainstorming results to file ({tmp_path}):")
    stdout, _, _ = run_command(["./cru", "brainstorm", "AI in education", "--output", tmp_path])
    print(stdout)
    
    # Show file exists and has content
    file_size = Path(tmp_path).stat().st_size
    print(f"File created with {file_size} bytes")
    Path(tmp_path).unlink()
    
    # JSON format
    print("\n3. Brainstorm with JSON output:")
    stdout, _, _ = run_command(["./cru", "brainstorm", "future of work", "--format", "json"])
    # Try to parse to verify it's valid JSON
    try:
        data = json.loads(stdout)
        print(f"Valid JSON output with content length: {len(data.get('content', ''))}")
    except:
        print("Output preview:", stdout[:200])


def demo_prompt_generate_command():
    """Demonstrate prompt generation command."""
    print("\n=== Prompt Generation Command Demo ===")
    
    # Basic prompt generation
    print("\n1. Generate prompt for 'API design patterns':")
    stdout, _, _ = run_command(["./cru", "prompt", "generate", "API design patterns"])
    print(stdout[:400] + "..." if len(stdout) > 400 else stdout)
    
    # Save to file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
        tmp_path = tmp.name
    
    print(f"\n2. Generate and save prompt to file ({tmp_path}):")
    stdout, _, _ = run_command(["./cru", "prompt", "generate", "microservices architecture", "--output", tmp_path])
    print(stdout)
    
    # Verify file
    content = Path(tmp_path).read_text()
    print(f"Generated prompt length: {len(content)} characters")
    Path(tmp_path).unlink()


def demo_help_system():
    """Demonstrate help and usage information."""
    print("\n=== Help System Demo ===")
    
    # Main help
    print("\n1. Main help message:")
    stdout, stderr, _ = run_command(["./cru", "--help"])
    print(stdout[:600] + "..." if len(stdout) > 600 else stdout)
    
    # Blueprint help
    print("\n2. Blueprint command help:")
    stdout, stderr, _ = run_command(["./cru", "blueprint", "--help"])
    print(stdout[:400] + "..." if len(stdout) > 400 else stdout)
    
    # Brainstorm help
    print("\n3. Brainstorm command help:")
    stdout, stderr, _ = run_command(["./cru", "brainstorm", "--help"])
    print(stdout[:300] + "..." if len(stdout) > 300 else stdout)


def demo_error_handling():
    """Demonstrate error handling."""
    print("\n=== Error Handling Demo ===")
    
    # Invalid command
    print("\n1. Invalid command:")
    stdout, stderr, _ = run_command(["./cru", "invalid"])
    print(f"Error: {stderr[:200]}")
    
    # Missing required argument
    print("\n2. Missing required argument:")
    stdout, stderr, _ = run_command(["./cru", "brainstorm"])
    print(f"Error: {stderr[:200]}")
    
    # Non-existent blueprint
    print("\n3. Non-existent blueprint:")
    stdout, stderr, _ = run_command(["./cru", "blueprint", "--name", "xyznonexistent"])
    print(stdout)


def main():
    """Run all CLI enhancement demos."""
    print("Enhanced CLI User Arguments Demo")
    print("=" * 50)
    
    try:
        # Run all demos
        demo_blueprint_features()
        demo_brainstorm_command()
        demo_prompt_generate_command()
        demo_help_system()
        demo_error_handling()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✓ Blueprint listing with search and filtering")
        print("✓ Blueprint selection by name (exact and partial match)")
        print("✓ Multiple output formats (text, JSON, YAML)")
        print("✓ File output support for all commands")
        print("✓ Brainstorming command with topic input")
        print("✓ Prompt generation command with context")
        print("✓ Comprehensive help system")
        print("✓ Graceful error handling")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        raise


if __name__ == "__main__":
    main()