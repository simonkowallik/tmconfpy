# -*- coding: utf-8 -*-
"""Test __main__.py"""

import runpy

import pytest  # pylint: disable=unused-import


def test_main(mocker):
    """test __main__.py, mock actual cli function and just check if it gets called."""
    cli = mocker.patch("tmconfpy.cli.cli")
    runpy.run_module("tmconfpy", run_name="__main__")
    assert cli.called is True
