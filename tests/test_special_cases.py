# -*- coding: utf-8 -*-
"""Test Special Cases"""
# pylint: disable=line-too-long,missing-function-docstring

import pytest  # pylint: disable=unused-import

from tmconfpy.parser import Parser

SPECIAL_CASES = {
    "irule": (
        r"""
ltm other /Common/other1 {}
ltm rule /Common/rule1 {
when CLIENT_ACCEPTED priority 1 {
log local0. "Client accepted"
}
}
ltm other /Common/other2 {}
""",
        {
            "ltm other /Common/other1": {},
            "ltm rule /Common/rule1": 'when CLIENT_ACCEPTED priority 1 {\nlog local0. "Client accepted"\n}',
            "ltm other /Common/other2": {},
        },
    ),
    "gtm_topology": (
        r"""
gtm topology ldns: subnet 192.0.0.0/16 server: country AQ {
    order 1
}
gtm topology ldns: continent EU server: country AQ {
    order 2
}
gtm global-settings load-balancing {
    topology-longest-match no
}
""",
        {
            "gtm global-settings load-balancing": {"topology-longest-match": "no"},
            "gtm topology /Common/Shared/topology": {
                "records": {
                    "longest-match-enabled": "no",
                    "topology_0": {
                        "destination": "country " "AQ",
                        "order": "1",
                        "source": "subnet " "192.0.0.0/16",
                    },
                    "topology_1": {
                        "destination": "country " "AQ",
                        "order": "2",
                        "source": "continent " "EU",
                    },
                }
            },
        },
    ),
    "gtm_other": (
        r"""
gtm global-settings general {
    ignore-ltm-rate-limit-modes { object-source destination }
}
gtm monitor external /Common/mon_gtm_ext {
    args "arg1 arg2 arg3"
    defaults-from /Common/external
    interval 30
    probe-timeout 5
    run /Common/external_monitor.script
    timeout 120
    user-defined var1 val
    user-defined var2 val2
}
""",
        {
            "gtm global-settings general": {
                "ignore-ltm-rate-limit-modes": ["object-source", "destination"]
            },
            "gtm monitor external /Common/mon_gtm_ext": {
                "args": '"arg1 arg2 arg3"',
                "defaults-from": "/Common/external",
                "interval": "30",
                "probe-timeout": "5",
                "run": "/Common/external_monitor.script",
                "timeout": "120",
                "user-defined": {"var1": "val", "var2": "val2"},
            },
        },
    ),
    "ltm_monitor": (
        r"""
ltm pool /Common/pool_monitor_min {
    monitor min 2 of { /Common/tcp /Common/tcp_half_open }
}
""",
        {
            "ltm pool /Common/pool_monitor_min": {
                "monitor min 2 of": ["/Common/tcp", "/Common/tcp_half_open"]
            }
        },
    ),
    "empty_object": (
        r"""
ltm empty object {}
ltm empty object2 { }
""",
        {
            "ltm empty object": {},
            "ltm empty object2": {},
        },
    ),
    "coerce unnamed objects": (
        r"""
module /Common/object {
    key value
    two_objects {
        {
            obj 1
        }
        {
            obj 2
        }
    }
    key2 value2
}
""",
        {
            "module /Common/object": {
                "key": "value",
                "two_objects": {"0": {"obj": "1"}, "1": {"obj": "2"}},
                "key2": "value2",
            }
        },
    ),
}


@pytest.mark.parametrize(
    "test_data, expected_result",
    [(SPECIAL_CASES[key][0], SPECIAL_CASES[key][1]) for key in SPECIAL_CASES.keys()],
)
def test_special_cases(test_data, expected_result):
    parser = Parser(test_data)
    print(parser.dict)
    assert parser.dict == expected_result
