# -*- coding: utf-8 -*-
"""Test Issues"""
# pylint: disable=line-too-long,missing-function-docstring

import pytest  # pylint: disable=unused-import

from tmconfpy.parser import Parser

ISSUES = {
    "issue-4-escaping": (
        r"""
ltm other /Common/other1 {}
ltm rule /Common/rule1 {
when HTTP_REQUEST priority 1 {
set user [regsub -nocase {^domain\\} [HTTP::username] ""]
}
}
ltm other /Common/other2 {}
""",
        {
            "ltm other /Common/other1": {},
            "ltm rule /Common/rule1": 'when HTTP_REQUEST priority 1 {\nset user [regsub -nocase {^domain\\} [HTTP::username] ""]\n}',
            "ltm other /Common/other2": {},
        },
    ),
}


@pytest.mark.parametrize(
    "test_data, expected_result",
    [(ISSUES[key][0], ISSUES[key][1]) for key in ISSUES.keys()],
)
def test_issues(test_data, expected_result):
    parser = Parser(test_data)
    print(parser.dict)
    assert parser.dict == expected_result
