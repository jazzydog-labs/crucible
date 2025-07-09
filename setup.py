#!/usr/bin/env python
"""Setup script for backward compatibility.

Modern Python projects should use pyproject.toml, but setup.py
is included for compatibility with older tools and workflows.
"""

from setuptools import setup

# All configuration is in pyproject.toml
setup()