"""Utilities for MS365 testing."""

import shutil

from custom_components.ms365_todo.integration.const_integration import DOMAIN

from ...const import STORAGE_LOCATION, TEST_DATA_INTEGRATION_LOCATION


def yaml_setup(tmp_path, infile):
    """Setup a yaml file"""
    fromfile = TEST_DATA_INTEGRATION_LOCATION / f"yaml/{infile}.yaml"
    tofile = tmp_path / STORAGE_LOCATION / f"{DOMAIN}s_test.yaml"
    shutil.copy(fromfile, tofile)


def check_yaml_file_contents(tmp_path, filename):
    """Check contents are what is expected."""
    path = tmp_path / STORAGE_LOCATION / f"{DOMAIN}s_test.yaml"
    with open(path, encoding="utf8") as file:
        created_yaml = file.read()
    path = TEST_DATA_INTEGRATION_LOCATION / f"yaml/{filename}.yaml"
    with open(path, encoding="utf8") as file:
        compare_yaml = file.read()
    assert created_yaml == compare_yaml
