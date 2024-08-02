#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Simon Kowallik
# License: Apache License 2.0

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: tmconf_get
author: Simon Kowallik (@simonkowallik)
short_description: Fetch tmconf configuration from BIG-IP TMOS device such as bigip.conf, making the configuration accessible as python data structures.
description:
- Ansible module to serialize F5 BIG-IP configuration files (C(bigip.conf) and similar) to a python data structures such as dict.
- The module returns the configuration as a dictionary, a tabular list and a tabular list with key-value pairs.
- The module can sort the configuration data using python C(sorted()) to make it easier to compare configurations.
- The module can be used to extract specific configuration parts from the BIG-IP configuration.
- The module can be used to save the configuration to JSON or YAML files.
version_added: 1.0.0
options:
  configfile:
    description:
    - The configuration file to be retrieved from the BIG-IP device.
    required: false
    default: /config/bigip.conf
    type: str
  sort:
    description:
    - Sort the configuration data using python sorted().
    - This is useful for comparing configurations.
    - The sorting is done in a recursive manner, all lists and dicts are sorted.
    required: false
    default: false
    type: bool
attributes:
    check_mode:
        description: This module does support check mode.
        support: full
    diff_mode:
        description: This module does not support diff mode as it does only fetch the configuration.
        support: none
notes:
- This module requires f5networks.f5_bigip httpapi connection plugin for communication with the BIG-IP.
- As this module copies configuration files from F5 BIG-IP devices, those configurations might contain sensitive data. Make sure YOU, as the implementer, *ensure* data security!
"""

EXAMPLES = r"""
- name: "Fetch /config/bigip_user.conf from BIG-IP device"
  simonkowallik.tmconfpy.tmconf_get:
    configfile: "/config/bigip_user.conf"
  register: config

- name: "Print root user if it exists in config.tmconf"
  ansible.builtin.debug:
    var: config.tmconf["auth user root"]
  when: '"auth user root" in config.tmconf'

- name: "Save config.tmconf to JSON file"
  ansible.builtin.copy:
    content: "{{ config.tmconf | to_nice_json }}"
    dest: ./bigip_user.json

- name: "Save config.tmconf to YAML file"
  ansible.builtin.copy:
    content: "{{ config.tmconf | to_nice_yaml }}"
    dest: ./bigip_user.yaml

- name: "Save config.tmconf to YAML file in tabular key value format"
  ansible.builtin.copy:
    content: "{{ config.tmconf_tabular_kv | to_nice_yaml }}"
    dest: ./bigip_user.yaml
"""

RETURN = r"""
tmconf:
  description: A dictionary representing the serialized BIG-IP configuration.
  returned: when success
  type: dict
tmconf_text:
    description: A string representing the un-serialized/raw BIG-IP configuration.
    returned: when success
    type: str
tmconf_tabular:
  description: A list representing the serialized BIG-IP configuration. Each element is a list containing the path, name and object.
  returned: when success
  type: list
  elements: list
  type: list
  elements: list
  contains:
    path:
      description: Object's path
      type: str
    name:
      description: Object's name
      type: str
    object:
      description: Object
      type: dict
tmconf_tabular_kv:
    description: A list representing the serialized BIG-IP configuration. Each element is a dict containing path:value, name:value and object:value elements.
    returned: when success
    type: list
    elements: dict
    contains:
        path:
            description: Object's path
            type: str
        name:
            description: Object's name
            type: str
        object:
            description: Object
            type: dict
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
        sort=dict(required=False, type="bool", default=False),
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
    tmconf_parsed = Parser(tmconf_text, sort=module.params["sort"])

    result = {"changed": False}

    result.update({"tmconf": tmconf_parsed.dict})
    result.update({"tmconf_text": tmconf_parsed.text})
    result.update({"tmconf_tabular": tmconf_parsed.tabular})
    result.update({"tmconf_tabular_kv": tmconf_parsed.tabular_kv})

    module.exit_json(**result)


if __name__ == "__main__":
    main()
