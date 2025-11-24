# setup.py
from setuptools import setup, find_packages
import os
from pathlib import Path

# Get current directory
current_dir = Path(__file__).parent

# Read README if it exists
readme_path = current_dir / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "CurveUp Toolchain - 3D to 2D fabric pattern generator"

# Read requirements if the file exists
requirements_path = current_dir / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = fh.read().splitlines()
else:
    requirements = [
        "PyQt5>=5.15.0",
        "trimesh>=3.9.0", 
        "numpy>=1.20.0",
        "scipy>=1.6.0",
        "pyvista>=0.32.0",
        "pyvistaqt>=0.7.0",
        "matplotlib>=3.3.0",
        "networkx>=2.5.0",
        "ezdxf>=0.17.0",
        "svgwrite>=1.4.0"
    ]

setup(
    name="curveup-toolchain",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Windows GUI toolchain for converting 3D objects to 2D fabric patterns",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/curveup-toolchain",
    packages=find_packages(where="src") if os.path.exists("src") else find_packages(),
    package_dir={"": "src"} if os.path.exists("src") else {},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Manufacturing",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "curveup=gui_main:main",
        ],
    },
    include_package_data=True,
)
