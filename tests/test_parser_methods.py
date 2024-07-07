# -*- coding: utf-8 -*-
"""Test test_parser_methods.py"""

import pytest  # pylint: disable=unused-import

from tmconfpy.parser import Parser

# pylint: disable=protected-access


class Test_ParserPrivateMethods:
    """Test Parser class static methods."""

    @staticmethod
    def test_count_indent():
        """Test _count_indent method."""
        assert Parser._count_indent("  hello") == 2
        assert Parser._count_indent("hello") == 0
        assert Parser._count_indent("  ") is None
        assert Parser._count_indent("") is None

    @staticmethod
    def test_remove_indent():
        """Test _remove_indent method."""
        assert Parser._remove_indent(Parser, ["    hello", "    world"]) == [
            "hello",
            "world",
        ]
        assert Parser._remove_indent(Parser, ["    hello", "  world"]) == [
            "hello",
            "rld",
        ]
        assert Parser._remove_indent(Parser, ["hello", "world"]) == ["hello", "world"]

    @staticmethod
    def test_get_object_name():
        """Test _get_object_name method."""
        assert Parser._get_object_name("title {") == "title"
        assert Parser._get_object_name("this is a title { }") == "this is a title"
        assert Parser._get_object_name("this is a title {}") == "this is a title"

    @staticmethod
    def test_is_irule():
        """Test _is_irule method."""
        assert not Parser._is_irule("rule { }")
        assert Parser._is_irule("ltm rule {")
        assert Parser._is_irule("pem irule {")
        assert Parser._is_irule("gtm rule {")

    @staticmethod
    def test_obj_to_arr():
        """Test _obj_to_arr method."""
        assert Parser._obj_to_arr("key key2 { value value2 }") == ["value", "value2"]
        assert Parser._obj_to_arr("key { value }") == ["value"]
        assert Parser._obj_to_arr("key { }") == [""]
        assert Parser._obj_to_arr("key { value value2 value3 }") == [
            "value",
            "value2",
            "value3",
        ]

    @staticmethod
    def test_str_to_obj():
        """Test _str_to_obj method."""
        assert Parser._str_to_obj("key value") == {"key": "value"}
        assert Parser._str_to_obj("key value value2") == {"key": "value value2"}
        assert Parser._str_to_obj("key value value2 value3") == {
            "key": "value value2 value3"
        }
        assert Parser._str_to_obj("key") == {"key": ""}
        assert Parser._str_to_obj("key ") == {"key": ""}

    @staticmethod
    def test_arr_to_multiline_str():
        """Test _arr_to_multiline_str method."""
        assert Parser._arr_to_multiline_str(["key value ", "line1", "line2"]) == {
            "key": "value\nline1\nline2"
        }
        assert Parser._arr_to_multiline_str(
            ["key value value2", "line1", "line2", "line3"]
        ) == {"key": "value value2\nline1\nline2\nline3"}
        assert Parser._arr_to_multiline_str(["key value"]) == {"key": "value"}
        assert Parser._arr_to_multiline_str(["key value", ""]) == {"key": "value\n"}
        assert Parser._arr_to_multiline_str(["key value", "line1", ""]) == {
            "key": "value\nline1\n"
        }

    @staticmethod
    def test_arr_to_dict():
        """Test _arr_to_dict method."""
        assert Parser._arr_to_dict(
            [{"unique key": {"a": 1, "b": 2}}, {"unique key 2": {"c": 3, "d": 4}}]
        ) == {"unique key": {"a": 1, "b": 2}, "unique key 2": {"c": 3, "d": 4}}
