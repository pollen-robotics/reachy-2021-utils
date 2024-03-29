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
        "reachy-sdk",
    ],
    extras_require={
        "doc": ["sphinx"],
    },
    entry_points={
        "console_scripts": [
        ],
    },
    author="Pollen Robotics",
    author_email="contact@pollen-robotics.com",
    url="https://github.com/pollen-robotics/reachy-utils",
    description="Useful tools for Reachy 2021",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
