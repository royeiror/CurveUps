# src/__init__.py
from .gui_main import main
from .main_pipeline import CurveUpToolchain
from .parameterization import MeshParameterizer

__all__ = ['main', 'CurveUpToolchain', 'MeshParameterizer']
__version__ = '0.1.0'
