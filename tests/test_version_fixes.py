# -*- coding: utf-8 -*-
"""Test Special Cases"""
# pylint: disable=line-too-long,missing-function-docstring

import pytest  # pylint: disable=unused-import

from tmconfpy.parser import Parser


class TestVersion1_0_1:
    def test_curly_in_str(self):
        """Test curly braces in string"""
        test_config = r"""
security dos bot-signature "/Common/Some Signature" {
    risk high
    rule "a:\"{\";"
}
"""
        parser = Parser(test_config)
        assert parser.dict == {
            'security dos bot-signature "/Common/Some Signature"': {
                "risk": "high",
                "rule": '"a:\\"{\\";"',
            }
        }

    def test_curly_in_str2(self):
        """Test curly braces in string"""
        test_config = r"""
security dos bot-signature "/Common/Some Signature" {
    test "a b }"
    test2 " { { a b }}"
    test3 "\"{\"\{"
    test4 "\"}\"\}}"
}
"""
        parser = Parser(test_config)
        assert parser.dict == {
            'security dos bot-signature "/Common/Some Signature"': {
                "test": '"a b }"',
                "test2": '" { { a b }}"',
                "test3": '"\\"{\\"\\{"',
                "test4": '"\\"}\\"\\}}"',
            }
        }

    def test_irule(self):
        """Test curly braces in string"""
        test_config = r"""
ltm rule json {
when EVENT {
  set x {"none"}
  set y { }
  set z {
  }
  set j "{\
  \"x\": \"y\"\
}\n"
# curly after
}
# curly before
}
"""
        expected = {
            "ltm rule json": 'when EVENT {\n  set x {"none"}\n  set y { }\n  set z {\n  }\n  set j "{\\\n  \\"x\\": \\"y\\"\\\n}\\n"\n# curly after\n}\n# curly before'
        }
        parser = Parser(test_config)
        assert parser.dict == expected
