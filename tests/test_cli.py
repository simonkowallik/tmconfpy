# -*- coding: utf-8 -*-
"""Test CLI interface"""

import json
import sys
from unittest import mock

import pytest  # pylint: disable=unused-import

from tmconfpy import __projectname__
from tmconfpy.cli import cli


class TestCLI:
    @staticmethod
    def test_filepath(monkeypatch, capfd):
        """Test CLI with file_path argument."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                __projectname__,
                "./example/imap.tmconf",
            ],
        )
        cli()
        cli_output, _ = capfd.readouterr()
        assert json.loads(cli_output.rstrip()) == json.loads(
            open("./example/imap.tmconf.json", "rb").read().decode().rstrip()
        )

    @staticmethod
    def test_stdin_no_data(monkeypatch, capfd):
        """Test CLI with no data from stdin."""
        with mock.patch("sys.stdin", autospec=True):
            monkeypatch.setattr(
                sys,
                "argv",
                [
                    __projectname__,
                ],
            )
            with pytest.raises(SystemExit):
                cli()
            _, cli_error = capfd.readouterr()
            assert (
                cli_error.rstrip()
                == "No file_path given or input is empty. Use -h|--help for help."
            )

    @staticmethod
    def test_format_object(monkeypatch, capfd):
        """Test CLI with object format."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                __projectname__,
                "./example/imap.tmconf",
                "--format",
                "object",
            ],
        )
        cli()
        cli_output, _ = capfd.readouterr()
        assert json.loads(cli_output.rstrip()) == json.loads(
            open("./example/imap.tmconf.json", "rb").read().decode().rstrip()
        )

    @staticmethod
    def test_format_tabular(monkeypatch, capfd):
        """Test CLI with tabular format."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                __projectname__,
                "./example/imap.tmconf",
                "--format",
                "tabular",
            ],
        )
        cli()
        cli_output, _ = capfd.readouterr()
        assert json.loads(cli_output.rstrip()) == [
            ["ltm profile imap", "imap", {"activation-mode": "require"}]
        ]

    @staticmethod
    def test_format_jsonl(monkeypatch, capfd):
        """Test CLI with jsonl format."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                __projectname__,
                "./example/imap.tmconf",
                "--format",
                "jsonl",
            ],
        )
        cli()
        cli_output, _ = capfd.readouterr()
        assert (
            cli_output.rstrip()
            == r'{"path": "ltm profile imap", "name": "imap", "object": {"activation-mode": "require"}}'
        )
