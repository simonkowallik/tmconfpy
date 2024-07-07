# -*- coding: utf-8 -*-
"""Test test_module.py"""

import json

import pytest  # pylint: disable=unused-import

from tmconfpy import Parser, tabularTmconf

TEST_DATA = {
    "json": (
        """ltm data-group internal private_net {\n    records {\n        10.0.0.0/8 { }\n    }\n    type ip\n}""",
        r'{"ltm data-group internal private_net": {"records": {"10.0.0.0/8": {}}, "type": "ip"}}',
    ),
    "dict": (
        """ltm data-group internal private_net {\n    records {\n        10.0.0.0/8 { }\n    }\n    type ip\n}""",
        {
            "ltm data-group internal private_net": {
                "records": {"10.0.0.0/8": {}},
                "type": "ip",
            }
        },
    ),
    "tabular": (
        """ltm profile imap imap {\n    activation-mode require\n}\nltm profile pop3 pop3 {\n    activation-mode require\n}""",
        [
            tabularTmconf(
                path="ltm profile imap",
                name="imap",
                object={"activation-mode": "require"},
            ),
            tabularTmconf(
                path="ltm profile pop3",
                name="pop3",
                object={"activation-mode": "require"},
            ),
        ],
    ),
    "tabular_json": (
        """ltm profile imap imap {\n    activation-mode require\n}\nltm profile pop3 pop3 {\n    activation-mode require\n}""",
        '[["ltm profile imap", "imap", {"activation-mode": "require"}], ["ltm profile pop3", "pop3", {"activation-mode": "require"}]]',
    ),
    "jsonl": (
        """ltm profile imap imap {\n    activation-mode require\n}\nltm profile pop3 pop3 {\n    activation-mode require\n}""",
        '{"path": "ltm profile imap", "name": "imap", "object": {"activation-mode": "require"}}\n{"path": "ltm profile pop3", "name": "pop3", "object": {"activation-mode": "require"}}',
    ),
}


class TestPublicModuleInterface:
    """Test Public Module Interface of tmconfpy.parser.Parser."""

    @pytest.mark.parametrize("testdata, expected", [TEST_DATA["json"]])
    def test_json(self, testdata, expected):
        """Test json property."""
        parser = Parser(testdata)
        assert json.loads(parser.json) == json.loads(expected)

    @pytest.mark.parametrize("testdata, expected", [TEST_DATA["dict"]])
    def test_dict(self, testdata, expected):
        """Test dict property."""
        parser = Parser(testdata)
        assert parser.dict == expected

    @pytest.mark.parametrize("testdata, expected", [TEST_DATA["tabular"]])
    def test_tabular(self, testdata, expected):
        """Test tabular property."""
        parser = Parser(testdata)
        assert parser.tabular == expected

    @pytest.mark.parametrize("testdata, expected", [TEST_DATA["tabular_json"]])
    def test_tabular_json(self, testdata, expected):
        """Test tabular_json property."""
        parser = Parser(testdata)
        assert json.loads(parser.tabular_json) == json.loads(expected)

    @pytest.mark.parametrize("testdata, expected", [TEST_DATA["jsonl"]])
    def test_jsonl(self, testdata, expected):
        """Test jsonl property."""
        parser = Parser(testdata)
        assert parser.jsonl == expected
