#!/usr/bin/env python3
"""
Setup script pour le projet N2F Synchronization.
Facilite les imports et l'installation du projet.
"""

from setuptools import setup, find_packages
import os

# Lire le README pour la description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Lire les requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="n2f-sync",
    version="2.0.0",
    author="N2F Team",
    description="Système de synchronisation entre Agresso et N2F",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "n2f-sync=python.sync_agresso_n2f:main",
        ],
    },
)
