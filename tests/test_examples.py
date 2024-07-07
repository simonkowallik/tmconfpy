# -*- coding: utf-8 -*-
"""Test test_parser_helper_methods.py"""

import json
import logging

import pytest  # pylint: disable=unused-import

from tmconfpy.parser import Parser


def read_file(file_path):
    """Read file and return content as string."""
    with open(file_path, "rb") as file:
        return file.read().decode()


def read_json_file(file_path):
    """Read file and return content as json object."""
    return json.loads(read_file(file_path))


def compare_json(file_path, json_obj):
    """Compare json object with json file content."""
    json_obj = json.loads(json_obj)
    return json_obj == read_json_file(file_path)


class TestExamples:
    @staticmethod
    def test_imap():
        """Test IMAP example."""
        parser = Parser(tmconf="example/imap.tmconf", is_filepath=True)
        assert compare_json("example/imap.tmconf.json", parser.json)

    @staticmethod
    def test_pop3():
        """Test POP3 example."""
        parser = Parser(tmconf="example/pop3.tmconf", is_filepath=True)
        assert compare_json("example/pop3.tmconf.json", parser.json)


class TestExamplesTmconf:
    class CustomLogHandler(logging.Handler):
        """Custom log handler to store log messages."""

        def __init__(self):
            super().__init__()
            self.log_messages = []

        def emit(self, record):
            print(self.format(record))
            self.log_messages.append(self.format(record))

    def test_tmconf(self):
        """Test advanced tmconf example."""
        custom_handler = self.CustomLogHandler()
        custom_handler.setFormatter(logging.Formatter("%(message)s"))
        parser_logger = logging.getLogger()
        parser_logger.addHandler(custom_handler)

        tmconf_log = read_file("example/test.tmconf.log").splitlines()

        parser = Parser(tmconf="example/test.tmconf", is_filepath=True)

        assert compare_json("example/test.tmconf.json", parser.json)

        assert len(tmconf_log) == len(custom_handler.log_messages)

        for test_log_entry in custom_handler.log_messages:
            for tmconf_log_entry in tmconf_log:
                status = False
                if test_log_entry in tmconf_log_entry:
                    status = True
                    break
            assert status
