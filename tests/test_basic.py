# tests/test_basic.py
import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main_pipeline import CurveUpToolchain

def test_toolchain_initialization():
    """Test that the toolchain initializes correctly"""
    toolchain = CurveUpToolchain()
    assert toolchain.input_mesh is None
    assert toolchain.parameterized_mesh is None
    assert toolchain.optimized_pattern is None

def test_mesh_loading():
    """Test mesh loading functionality"""
    toolchain = CurveUpToolchain()
    # This would require a test mesh file
    # You can create a simple test cube programmatically
    pass

# tests/__init__.py
# Empty file to make tests a package
