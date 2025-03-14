#!/usr/bin/env python
"""
RF Layout: YAML to GDSII Conversion Tool

A solution for RFIC designers to define complex RF circuits using a human-readable
YAML format, which will then be automatically translated into industry-standard 
GDSII layout files.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rf_layout",
    version="0.1.0",
    author="RF Layout Team",
    author_email="info@rflayout.org",
    description="YAML to GDSII conversion tool for RF circuit layouts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rflayout/rf_layout",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)"
    ],
    python_requires=">=3.6",
    install_requires=[
        "gdspy>=1.6.0",
        "numpy>=1.19.0",
        "pyyaml>=5.1.0",
        "jsonschema>=3.2.0",
    ],
    entry_points={
        'console_scripts': [
            'rf_layout=rf_layout.main:main',
        ],
    }
)