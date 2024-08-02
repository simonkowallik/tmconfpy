# -*- coding: utf-8 -*-
"""Test test_parser_methods.py"""

import pytest  # pylint: disable=unused-import

from tmconfpy.parser import Parser

# pylint: disable=protected-access


class Test_Sorting:
    """Test Sorting class static methods."""

    test_data = r"""
ltm profile profile-type OtherProfile { }
ltm profile profile-type MyProfile {
    alert enabled
    cache disabled
    allow-dynamic disabled
    object {
        zzz value
        aaa value
        bbb-list { a c b }
    }
    options { ccc aaa zzz }
}
"""
    expected_result = {
        "ltm profile profile-type OtherProfile": {},
        "ltm profile profile-type MyProfile": {
            "alert": "enabled",
            "cache": "disabled",
            "allow-dynamic": "disabled",
            "object": {"zzz": "value", "aaa": "value", "bbb-list": ["a", "c", "b"]},
            "options": ["ccc", "aaa", "zzz"],
        },
    }

    expected_result_sorted = {
        "ltm profile profile-type MyProfile": {
            "alert": "enabled",
            "allow-dynamic": "disabled",
            "cache": "disabled",
            "object": {"aaa": "value", "zzz": "value", "bbb-list": ["a", "b", "c"]},
            "options": ["aaa", "ccc", "zzz"],
        },
        "ltm profile profile-type OtherProfile": {},
    }

    def test_unsorted(self):
        """Test sort_dict method."""
        parsed = Parser(self.test_data)
        assert parsed.dict == self.expected_result

    def test_sorted(self):
        """Test sort_dict method."""
        parsed = Parser(self.test_data, sort=True)
        assert parsed.dict == self.expected_result_sorted
