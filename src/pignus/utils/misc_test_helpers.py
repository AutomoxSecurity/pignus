"""Misc Test helpers

Testing
Unit Tests at automox/pignus/tests/unit/utils/test_misc_test_helpers.py

Usage to save JSON as file
from pignus.utils import misc_test_helpers
misc_test_helpers.save_json_file(json, phile)

"""
import os
import json

from pignus.utils import log


def load_json_file(phile: str):
    """Load a JSON file as a Python dictionary.
    :unit-test: test__load_json_file
    """
    path = os.path.join(
        os.environ.get("PIGNUS_PATH"),
        phile
    )
    if not os.path.exists(path):
        log.error("Path does not exist: %s" % path)
        return False
    phile_obj = open(path)
    try:
        phile = read_file(path)
        phile_json = json.loads(phile_obj.read())
        return phile_json
    except json.decoder.JSONDecodeError:
        return False


def save_json_file(json_to_save: dict, file_path: str) -> str:
    """Takes a Python dict and saves it as a json file."""
    # dump = json.dumps(json_to_save, indent=4)
    with open(file_path, "w") as outfile:
        json.dump(json_to_save, outfile)
    return True


def read_file(file_to_open: str) -> str:
    """Reads a file from a path relative to the method calling this method."""
    pignus_path = os.environ.get("PIGNUS_PATH")
    if not pignus_path:
        raise AttributeError
    path_to_open = os.path.join(
        pignus_path,
        file_to_open)
    if not os.path.exists(path_to_open):
        log.error("Path does not exist: %s" % path_to_open)
        return False
    phile = open(path_to_open).read()
    return phile

# End File: automox/pignus/src/pignus/utils/misc_test_helpers.py
