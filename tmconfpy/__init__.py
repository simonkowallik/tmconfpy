# -*- coding: utf-8 -*-
"""Top-level package for tmconfpy."""

from .parser import Parser, tabularTmconf

__all__ = [
    "Parser",
    "tabularTmconf",
]
__author__ = """Simon Kowallik"""
__email__ = "sk-github@simonkowallik.com"
__version__ = "1.0.0"  # pyproject.toml
__projectname__ = "tmconfpy"
# pylint: disable=line-too-long
__description__ = "A Python library to serialize F5 BIG-IP configuration files to a python dict or JSON."
__license__ = "Apache 2.0"
__homepage__ = "https://github.com/simonkowallik/tmconfpy"
