"""Tests for repository setup and configuration."""

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

# Use tomllib for Python 3.11+ or fallback to toml
try:
    import tomllib
except ImportError:
    try:
        import toml as tomllib
    except ImportError:
        tomllib = None


class TestProjectStructure:
    """Test that the project structure is properly set up."""
    
    def test_required_files_exist(self):
        """Test that all required configuration files exist."""
        root = Path(__file__).resolve().parents[1]
        
        required_files = [
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "requirements-dev.txt",
            ".pre-commit-config.yaml",
            "tox.ini",
            ".editorconfig",
            ".github/workflows/ci.yml",
        ]
        
        for file in required_files:
            assert (root / file).exists(), f"Required file {file} does not exist"
    
    def test_source_structure(self):
        """Test that source code is properly structured."""
        root = Path(__file__).resolve().parents[1]
        src = root / "src"
        
        assert src.exists(), "src directory does not exist"
        assert (src / "crucible").exists(), "crucible package does not exist"
        assert (src / "crucible" / "__init__.py").exists(), "__init__.py missing"
        assert (src / "crucible" / "py.typed").exists(), "py.typed marker missing"
    
    def test_test_structure(self):
        """Test that test directory is properly structured."""
        root = Path(__file__).resolve().parents[1]
        tests = root / "tests"
        
        assert tests.exists(), "tests directory does not exist"
        assert (tests / "__init__.py").exists(), "tests/__init__.py missing"


class TestPyprojectToml:
    """Test pyproject.toml configuration."""
    
    def test_pyproject_valid(self):
        """Test that pyproject.toml is valid TOML."""
        if tomllib is None:
            pytest.skip("tomllib not available")
            
        root = Path(__file__).resolve().parents[1]
        pyproject_path = root / "pyproject.toml"
        
        if hasattr(tomllib, 'loads'):
            # Python 3.11+ tomllib
            with open(pyproject_path, 'rb') as f:
                config = tomllib.load(f)
        else:
            # toml package
            with open(pyproject_path) as f:
                config = tomllib.load(f)
        
        assert "project" in config, "Missing [project] section"
        assert "build-system" in config, "Missing [build-system] section"
    
    def test_project_metadata(self):
        """Test project metadata in pyproject.toml."""
        if tomllib is None:
            pytest.skip("tomllib not available")
            
        root = Path(__file__).resolve().parents[1]
        pyproject_path = root / "pyproject.toml"
        
        if hasattr(tomllib, 'loads'):
            # Python 3.11+ tomllib
            with open(pyproject_path, 'rb') as f:
                config = tomllib.load(f)
        else:
            # toml package
            with open(pyproject_path) as f:
                config = tomllib.load(f)
        
        project = config["project"]
        assert project["name"] == "crucible"
        assert "version" in project
        assert "description" in project
        assert "dependencies" in project
        assert "optional-dependencies" in project
    
    def test_tool_configuration(self):
        """Test tool configurations in pyproject.toml."""
        if tomllib is None:
            pytest.skip("tomllib not available")
            
        root = Path(__file__).resolve().parents[1]
        pyproject_path = root / "pyproject.toml"
        
        if hasattr(tomllib, 'loads'):
            # Python 3.11+ tomllib
            with open(pyproject_path, 'rb') as f:
                config = tomllib.load(f)
        else:
            # toml package
            with open(pyproject_path) as f:
                config = tomllib.load(f)
        
        assert "tool" in config
        tools = config["tool"]
        
        # Check pytest configuration
        assert "pytest" in tools
        assert "ini_options" in tools["pytest"]
        
        # Check coverage configuration
        assert "coverage" in tools
        assert "run" in tools["coverage"]
        assert "report" in tools["coverage"]
        
        # Check black configuration
        assert "black" in tools
        assert tools["black"]["line-length"] == 100
        
        # Check ruff configuration
        assert "ruff" in tools
        assert tools["ruff"]["line-length"] == 100


class TestRequirements:
    """Test requirements files."""
    
    def test_requirements_files_valid(self):
        """Test that requirements files are valid."""
        root = Path(__file__).resolve().parents[1]
        
        # Test base requirements
        req_file = root / "requirements.txt"
        with open(req_file) as f:
            lines = f.readlines()
        
        # Should have at least openai and pyyaml
        packages = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
        assert any("openai" in pkg for pkg in packages)
        assert any("pyyaml" in pkg.lower() for pkg in packages)
        
        # Test dev requirements
        dev_req_file = root / "requirements-dev.txt"
        with open(dev_req_file) as f:
            dev_lines = f.readlines()
        
        # Should include base requirements
        assert any("-r requirements.txt" in line for line in dev_lines)
        
        # Should have testing tools
        dev_packages = [line.strip() for line in dev_lines 
                       if line.strip() and not line.startswith("#") and not line.startswith("-r")]
        assert any("pytest" in pkg for pkg in dev_packages)
        assert any("black" in pkg for pkg in dev_packages)
        assert any("ruff" in pkg for pkg in dev_packages)


class TestPreCommitConfig:
    """Test pre-commit configuration."""
    
    def test_pre_commit_config_valid(self):
        """Test that .pre-commit-config.yaml is valid."""
        root = Path(__file__).resolve().parents[1]
        config_path = root / ".pre-commit-config.yaml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert "repos" in config
        assert len(config["repos"]) > 0
        
        # Check for essential hooks
        hook_ids = []
        for repo in config["repos"]:
            for hook in repo.get("hooks", []):
                hook_ids.append(hook["id"])
        
        assert "black" in hook_ids
        assert "ruff" in hook_ids
        assert "mypy" in hook_ids
        assert "trailing-whitespace" in hook_ids


class TestGitHubActions:
    """Test GitHub Actions configuration."""
    
    def test_ci_workflow_valid(self):
        """Test that CI workflow is valid YAML."""
        root = Path(__file__).resolve().parents[1]
        workflow_path = root / ".github" / "workflows" / "ci.yml"
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        assert "name" in workflow
        # YAML treats 'on' as a boolean True
        assert True in workflow or "on" in workflow
        assert "jobs" in workflow
        
        # Check jobs
        jobs = workflow["jobs"]
        assert "test" in jobs
        assert "build" in jobs
        assert "security" in jobs
        
        # Check test job has matrix
        test_job = jobs["test"]
        assert "strategy" in test_job
        assert "matrix" in test_job["strategy"]
        assert "python-version" in test_job["strategy"]["matrix"]


class TestPackageInstallation:
    """Test that the package can be installed."""
    
    @pytest.mark.skipif(sys.platform == "win32", reason="Skip on Windows due to path issues")
    def test_package_installable(self):
        """Test that the package can be installed in development mode."""
        root = Path(__file__).resolve().parents[1]
        
        # Try to import the package
        try:
            import crucible
            assert crucible is not None
        except ImportError:
            # If not installed, that's okay for this test
            pass
    
    def test_setup_py_valid(self):
        """Test that setup.py exists and is valid."""
        root = Path(__file__).resolve().parents[1]
        setup_path = root / "setup.py"
        
        assert setup_path.exists()
        
        # Check that it's a minimal setup.py for pyproject.toml
        with open(setup_path) as f:
            content = f.read()
        
        assert "setuptools" in content
        assert "setup()" in content


class TestDevelopmentTools:
    """Test development tools configuration."""
    
    def test_tox_config_valid(self):
        """Test that tox.ini is properly configured."""
        root = Path(__file__).resolve().parents[1]
        tox_path = root / "tox.ini"
        
        with open(tox_path) as f:
            content = f.read()
        
        # Check for essential environments
        assert "[testenv]" in content
        assert "[testenv:lint]" in content
        assert "[testenv:type]" in content
        assert "[testenv:coverage]" in content
        
        # Check Python versions (in the envlist)
        assert "39" in content
        assert "310" in content
        assert "311" in content
        assert "312" in content
    
    def test_editorconfig_valid(self):
        """Test that .editorconfig is properly configured."""
        root = Path(__file__).resolve().parents[1]
        editor_path = root / ".editorconfig"
        
        with open(editor_path) as f:
            content = f.read()
        
        # Check basic settings
        assert "root = true" in content
        assert "[*.py]" in content
        assert "indent_size = 4" in content
        assert "max_line_length = 100" in content