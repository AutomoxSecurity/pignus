#!/usr/bin/env python3

from setuptools import setup
from pignus import version

setup(
    name="Pignus",
    version=version.__version__,
    description="Pignus",
    author="Automox",
    author_email="alix.fullerton@automox.com",
    url="https://github.com/PatchSimple/pignus",
    packages=[
        "pignus",
        "pignus.api",
        "pignus.api.models",
        "pignus.api.collections",
        "pignus.client",
        "pignus.collections",
        "pignus.display",
        "pignus.parse",
        "pignus.models",
        "pignus.utils",
        "pignus.utils.test",
        "pignus.parse",
        "pignus.sentry",
        "pignus.cli",
    ],
    scripts=["scripts/pignus"],
)

# End File: automox/pignus/src/pignus/setup.py
