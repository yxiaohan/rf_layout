"""
Pytest configuration file for RF Layout tests.
"""

import os
import pytest
import tempfile
import shutil

@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory"""
    return os.path.join(os.path.dirname(__file__), "fixtures")

@pytest.fixture(scope="session")
def test_design_yaml(test_data_dir):
    """Return path to test design YAML file"""
    return os.path.join(test_data_dir, "test_design.yaml")

@pytest.fixture(scope="session")
def test_tech_yaml(test_data_dir):
    """Return path to test technology rules file"""
    return os.path.join(test_data_dir, "test_tech.yaml")

@pytest.fixture(scope="function")
def temp_dir():
    """Create a temporary directory for test outputs"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def output_gds(temp_dir):
    """Return path for test GDS output"""
    return os.path.join(temp_dir, "test_output.gds")