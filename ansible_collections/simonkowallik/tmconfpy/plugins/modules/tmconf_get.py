#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: tmconf_get
author: Simon Kowallik
short_description: Fetch tmconf configuration from BIG-IP TMOS device such as bigip.conf, making the configuration accessible as python data structures.
description:
- Ansible module to serialize F5 BIG-IP configuration files (bigip.conf and similar) to a python data structures such as dict.
version_added: 1.0.0
options:
  configfile:
    description:
    - The configuration file to be retrieved from the BIG-IP device.
    required: false
    default: /config/bigip.conf
    type: str
  format:
    description:
    - C(format) specifies the structure of the configuration data retrieved.
    - With value C(object), the default, the configuration will be accessible as a simple dict.
    - With value C(tabular) the configuration will be accessible as a list of lists, each containing the object path, object name and object.
    type: str
    required: false
    default: object
    choices:
    - object
    - tabular
notes:
- This module requires f5networks.f5_bigip httpapi connection plugin for communication with the BIG-IP.
- As this module copies configuration files from F5 BIG-IP devices, those configurations might contain sensitive data. Make sure YOU, as the implementor, *ensure* data security!
"""

EXAMPLES = r"""
- name: "Fetch bigip_user.conf in tabular format"
    simonkowallik.tmconfpy.tmconf_get:
    configfile: /config/bigip_user.conf
    format: tabular
    register: tabular_config

- name: "Print bigip_user.conf in tabular format"
    ansible.builtin.debug:
    var: tabular_config.tmconf_tabular

- name: "Fetch bigip_user.conf"
    simonkowallik.tmconfpy.tmconf_get:
    configfile: /config/bigip_user.conf
    register: config

- name: "Print bigip_user.conf"
    ansible.builtin.debug:
    var: config.tmconf

"""

RETURN = r"""
tmconf:
  description: A dictionary representing the serialized BIG-IP configuration.
  returned: when parameter 'format' is set to 'object'
  type: dict
  sample: |
    {
        "auth user admin": {
            "description": "\"Admin User\"",
            "partition-access": {
                "all-partitions": {
                    "role": "admin"
                }
            },
            "session-limit": "-1",
            "shell": "bash"
        },
        "auth user root": {
            "description": "root",
            "session-limit": "-1",
            "shell": "bash"
        }
    }
tmconf_tabular:
  description: A list representing the serialized BIG-IP configuration. Each element is a list containing the object path, object name and object.
  returned: when parameter 'format' is set to 'tabular'
  type: list
  elements: list
  type: list
  elements: list
  contains:
      - description: Object path
        type: str
      - description: Object name
        type: str
      - description: Object
        type: dict
  sample: |
    [
        [
            "auth user",
            "admin",
            {
                "description": "\"Admin User\"",
                "partition-access": {
                    "all-partitions": {
                        "role": "admin"
                    }
                },
                "session-limit": "-1",
                "shell": "bash"
            }
        ],
        [
            "auth user",
            "root",
            {
                "description": "root",
                "session-limit": "-1",
                "shell": "bash"
            }
        ]
    ]
"""

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import ConnectionError
from ansible_collections.simonkowallik.tmconfpy.plugins.module_utils.tmos_api import (
    APIClient,
    APIResultProcessor,
)

#from tmconfpy.parser import Parser
# vendored:
from ansible_collections.simonkowallik.tmconfpy.plugins.module_utils.parser import Parser

def main():
    """entry point for module execution"""
    argument_spec = dict(
        configfile=dict(required=False, type="str", default="/config/bigip.conf"),
        format=dict(
            required=False, type="str", default="object", choices=["object", "tabular"]
        ),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    api_client = APIClient(module)
    try:
        api_response = api_client.get(configfile=module.params["configfile"])
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))

    if api_response is None:
        module.fail_json(
            msg="Failed to retrieve the configfile.",
            error_details="The API response did not provide the expected data (contents, commandResult).",
        )
    elif api_response.startswith("NOT_A_FILE"):
        module.fail_json(
            msg="Failed to retrieve the configfile.",
            error_details=f"The specified file '{module.params['configfile']}' does not exist or is not a file.",
        )

    api_result_processor = APIResultProcessor(module, api_response)

    tmconf_text = api_result_processor.result
    tmconf_parsed = Parser(tmconf_text)

    result = {"changed": False}

    if module.params["format"] == "tabular":
        result.update({"tmconf_tabular": tmconf_parsed.tabular})
    else:
        result.update({"tmconf": tmconf_parsed.dict})

    module.exit_json(**result)


if __name__ == "__main__":
    main()
