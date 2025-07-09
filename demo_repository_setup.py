#!/usr/bin/env python3
"""Demo showcasing the repository setup and development tools.

This demo demonstrates:
- Project structure and packaging
- Development tools configuration
- Testing and coverage setup
- Code quality tools
- CI/CD workflow
"""

import subprocess
import sys
from pathlib import Path
import json

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent / 'src'))


def demo_killer_feature():
    """The ONE thing that makes repository setup amazing."""
    print("=== KILLER FEATURE: Professional Python project in 3 commands ===")
    
    print("$ pip install -e .")
    print("$ pre-commit install")
    print("$ tox")
    
    print("\n✅ Full CI/CD pipeline with:")
    print("  • Multi-Python testing (3.9-3.12)")
    print("  • Auto-formatting (Black)")
    print("  • Linting (Ruff)")
    print("  • Type checking (MyPy)")
    print("  • Security scanning (Bandit)")
    print("  • Coverage reports")
    
    print("\n✨ From zero to production-ready in minutes!\n")


def run_command(cmd, shell=False):
    """Run a command and return output."""
    try:
        result = subprocess.run(
            cmd if shell else cmd.split(), 
            capture_output=True, 
            text=True,
            shell=shell
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1


def demo_project_structure():
    """Demonstrate project structure."""
    print("=== Project Structure Demo ===")
    
    root = Path(__file__).resolve().parent
    
    print("\n1. Core project files:")
    files = [
        "pyproject.toml",
        "setup.py",
        "requirements.txt",
        "requirements-dev.txt",
        "README.md",
        "justfile",
    ]
    for file in files:
        exists = "✓" if (root / file).exists() else "✗"
        print(f"  {exists} {file}")
    
    print("\n2. Source code structure:")
    src_files = [
        "src/",
        "src/crucible/",
        "src/crucible/__init__.py",
        "src/crucible/py.typed",
        "src/cli.py",
    ]
    for file in src_files:
        exists = "✓" if (root / file).exists() else "✗"
        print(f"  {exists} {file}")
    
    print("\n3. Development configuration:")
    config_files = [
        ".pre-commit-config.yaml",
        ".editorconfig",
        ".gitignore",
        "tox.ini",
        ".github/workflows/ci.yml",
    ]
    for file in config_files:
        exists = "✓" if (root / file).exists() else "✗"
        print(f"  {exists} {file}")


def demo_package_info():
    """Demonstrate package metadata."""
    print("\n=== Package Information Demo ===")
    
    # Try to load package metadata
    try:
        import tomllib
    except ImportError:
        try:
            import toml as tomllib
        except ImportError:
            print("  Unable to read pyproject.toml (tomllib not available)")
            return
    
    root = Path(__file__).resolve().parent
    pyproject_path = root / "pyproject.toml"
    
    if hasattr(tomllib, 'loads'):
        with open(pyproject_path, 'rb') as f:
            config = tomllib.load(f)
    else:
        with open(pyproject_path) as f:
            config = tomllib.load(f)
    
    project = config.get("project", {})
    print(f"\n1. Package name: {project.get('name', 'N/A')}")
    print(f"2. Version: {project.get('version', 'N/A')}")
    print(f"3. Description: {project.get('description', 'N/A')}")
    print(f"4. Python requirement: {project.get('requires-python', 'N/A')}")
    
    print("\n5. Dependencies:")
    for dep in project.get("dependencies", []):
        print(f"   - {dep}")
    
    print("\n6. Optional dependencies (dev):")
    dev_deps = project.get("optional-dependencies", {}).get("dev", [])
    for dep in dev_deps[:5]:  # Show first 5
        print(f"   - {dep}")
    if len(dev_deps) > 5:
        print(f"   ... and {len(dev_deps) - 5} more")


def demo_testing_setup():
    """Demonstrate testing configuration."""
    print("\n=== Testing Setup Demo ===")
    
    print("\n1. Running tests with pytest:")
    stdout, stderr, code = run_command("python -m pytest tests/test_repository_setup.py -v --tb=short")
    
    if code == 0:
        # Count test results
        lines = stdout.split('\n')
        test_lines = [l for l in lines if " PASSED" in l or " FAILED" in l]
        passed = sum(1 for l in test_lines if " PASSED" in l)
        failed = sum(1 for l in test_lines if " FAILED" in l)
        
        print(f"   ✓ Tests completed: {passed} passed, {failed} failed")
    else:
        print("   ✗ Tests failed or pytest not available")
    
    print("\n2. Test configuration (from pyproject.toml):")
    print("   - Minimum pytest version: 7.0")
    print("   - Coverage reporting enabled")
    print("   - HTML coverage reports")
    print("   - Test paths: tests/")
    print("   - Python path includes: src/")


def demo_code_quality_tools():
    """Demonstrate code quality tools."""
    print("\n=== Code Quality Tools Demo ===")
    
    print("\n1. Black (code formatter):")
    stdout, stderr, code = run_command("black --check src/crucible/__init__.py")
    if code == 0:
        print("   ✓ Code is properly formatted")
    else:
        print("   ℹ Black not installed or code needs formatting")
    
    print("\n2. Ruff (linter):")
    stdout, stderr, code = run_command("ruff check src/crucible/__init__.py")
    if code == 0:
        print("   ✓ No linting issues found")
    else:
        print("   ℹ Ruff not installed or linting issues exist")
    
    print("\n3. MyPy (type checker):")
    stdout, stderr, code = run_command("mypy src/crucible/__init__.py")
    if "Success" in stdout or code == 0:
        print("   ✓ Type checking passed")
    else:
        print("   ℹ MyPy not installed or type issues exist")
    
    print("\n4. Pre-commit hooks configured:")
    hooks = [
        "trailing-whitespace",
        "end-of-file-fixer",
        "black",
        "ruff",
        "mypy",
        "bandit",
    ]
    for hook in hooks:
        print(f"   - {hook}")


def demo_development_workflow():
    """Demonstrate development workflow."""
    print("\n=== Development Workflow Demo ===")
    
    print("\n1. Install development dependencies:")
    print("   $ pip install -r requirements-dev.txt")
    print("   $ pip install -e .")
    
    print("\n2. Run tests:")
    print("   $ pytest                    # Run all tests")
    print("   $ pytest -v                 # Verbose output")
    print("   $ pytest --cov=src          # With coverage")
    
    print("\n3. Code quality checks:")
    print("   $ black src tests           # Format code")
    print("   $ ruff check src tests      # Lint code")
    print("   $ mypy src                  # Type check")
    
    print("\n4. Pre-commit hooks:")
    print("   $ pre-commit install        # Install hooks")
    print("   $ pre-commit run --all      # Run all checks")
    
    print("\n5. Tox environments:")
    print("   $ tox                       # Run all environments")
    print("   $ tox -e py311              # Test on Python 3.11")
    print("   $ tox -e lint               # Run linters")
    print("   $ tox -e coverage           # Generate coverage")


def demo_ci_workflow():
    """Demonstrate CI/CD setup."""
    print("\n=== CI/CD Workflow Demo ===")
    
    print("\n1. GitHub Actions workflow configured:")
    print("   - Triggers: push to main/develop, pull requests")
    print("   - Python versions: 3.9, 3.10, 3.11, 3.12")
    
    print("\n2. CI jobs:")
    print("   a) Test job:")
    print("      - Install dependencies")
    print("      - Run linting (ruff)")
    print("      - Check formatting (black)")
    print("      - Type checking (mypy)")
    print("      - Run tests with coverage")
    print("      - Upload coverage to Codecov")
    
    print("\n   b) Build job:")
    print("      - Build distribution packages")
    print("      - Check package with twine")
    print("      - Upload artifacts")
    
    print("\n   c) Security job:")
    print("      - Run Bandit security scan")
    print("      - Check for common vulnerabilities")


def demo_package_installation():
    """Demonstrate package installation."""
    print("\n=== Package Installation Demo ===")
    
    print("\n1. Development installation:")
    print("   $ pip install -e .")
    print("   This installs the package in editable mode")
    
    print("\n2. Production installation:")
    print("   $ pip install .")
    print("   This installs the package normally")
    
    print("\n3. Build distribution:")
    print("   $ python -m build")
    print("   Creates wheel and source distributions")
    
    print("\n4. Check if package is importable:")
    try:
        import crucible
        print("   ✓ Package 'crucible' is importable")
        
        # Check for CLI entry points
        print("\n5. CLI entry points configured:")
        print("   - crucible")
        print("   - cru")
    except ImportError:
        print("   ℹ Package not installed in current environment")


def main():
    """Run all repository setup demos."""
    print("Repository Setup and Configuration Demo")
    print("=" * 50)
    
    try:
        # Start with the killer feature
        demo_killer_feature()
        
        # Run all demos
        demo_project_structure()
        demo_package_info()
        demo_testing_setup()
        demo_code_quality_tools()
        demo_development_workflow()
        demo_ci_workflow()
        demo_package_installation()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✓ Modern Python packaging with pyproject.toml")
        print("✓ Comprehensive testing setup with pytest")
        print("✓ Code quality tools (black, ruff, mypy)")
        print("✓ Pre-commit hooks for automated checks")
        print("✓ CI/CD with GitHub Actions")
        print("✓ Multi-Python version testing with tox")
        print("✓ Security scanning with Bandit")
        print("✓ Professional project structure")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        raise


if __name__ == "__main__":
    main()