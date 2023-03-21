#!/usr/bin/env python
"""Setup config file."""

from os import path

from setuptools import find_packages, setup


here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="reachy-utils",
    version="0.1.0",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "PyYAML",
        "pypot",
        "reachy-sdk",
    ],
    extras_require={
        "doc": ["sphinx"],
    },
    entry_points={
        "console_scripts": [
            "orbita-zero-hardware = reachy_utils.orbita_zero_hardware:main",
            "reachy-discovery = reachy_utils.discovery:scan",
            "reachy-udev-rule-right-arm = reachy_utils.udev_rules:write_udev_rules_right_arm",
            "reachy-udev-rule-left-arm = reachy_utils.udev_rules:write_udev_rules_left_arm",
            "reachy-udev-rule-head = reachy_utils.udev_rules:write_udev_rules_head",
        ],
    },
    author="Pollen Robotics",
    author_email="contact@pollen-robotics.com",
    url="https://github.com/pollen-robotics/reachy-utils",
    description=".",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
