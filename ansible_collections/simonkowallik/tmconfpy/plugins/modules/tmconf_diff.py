#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Simon Kowallik
# License: Apache License 2.0

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: tmconf_diff
author: Simon Kowallik (@simonkowallik)
short_description: Compare two configurations using deepdiff and return the difference.
description:
- Ansible module to compare two configurations (config to reference) using the deepdiff library.
- The module returns the difference between two configurations in deepdiff format.
- If the configuration C(config) deviates from the C(reference), the module will return changed true.
version_added: 1.1.0
options:
  config:
    description:
    - The configuration to be compared to the reference configuration.
    required: true
    type: raw
  reference:
    description:
    - The reference configuration 'config' will be compared to.
    required: true
    type: raw
  deepdiff_args:
    description:
    - Additional arguments to be passed to deepdiff.DeepDiff.
    required: false
    type: list
    default: []
  deepdiff_kwargs:
    description:
    - Additional keyword arguments to be passed to deepdiff.DeepDiff.
    required: false
    type: dict
    default: {}
attributes:
    check_mode:
        description: This module does support check mode.
        support: full
    diff_mode:
        description: This module does support diff mode.
        support: full
notes:
- This module requires the deepdiff python package to be installed on the ansible controller.
"""

EXAMPLES = r"""
- name: "Fetch /config/bigip.conf from BIG-IP device"
  simonkowallik.tmconfpy.tmconf_get:
    configfile: "/config/bigip.conf"
  register: bigip_conf

- name: "Extract relevant configuration"
  ansible.builtin.set_fact:
    # Using tmconf_tabular_kv to get a more structured output that is easier to query
    sys_autocheck_config: "{{ bigip_conf.tmconf_tabular_kv | community.general.json_query(sys_autocheck_query) }}"
  vars:
    sys_autocheck_query: "[?path=='sys software'].{name: name, object: object}[?name=='update'].object.\"auto-check\""

- name: "Compare sys software update configuration to reference using tmconf_diff"
  simonkowallik.tmconfpy.tmconf_diff:
    config: "{{ sys_autocheck_config }}"
    reference: [ "enabled" ]
    # ignore order of lists and dicts, be verbose about changes, see: https://zepworks.com/deepdiff/current/basics.html
    deepdiff_kwargs: {"ignore_order": true, "verbose_level": 2}
  #failed_when: tmconf_diff_result.changed  # force failure if configuration deviates from reference
  register: tmconf_diff_result

- name: "Print tmconf_diff result"
  ansible.builtin.debug:
    msg: "{{ tmconf_diff_result.deepdiff }}"
"""

RETURN = r"""
deepdiff:
    description: A dictionary describing what is either missing, added or changed in C(config) compared to C(reference) using the deepdiff format.
    returned: when success
    type: dict
    sample:
        {
            "deepdiff": {
                "iterable_item_removed": {
                    "root[1]['object']['options'][1]": "no-tlsv1"
                }
            }
        }
"""

from ansible.module_utils.basic import AnsibleModule

#from deepdiff import DeepDiff
try:
    from deepdiff import DeepDiff
    HAS_DEEPDIFF = True
except ImportError:
    HAS_DEEPDIFF = False

def main():
    """entry point for module execution"""
    argument_spec = dict(
        config=dict(required=True, type="raw"),
        reference=dict(required=True, type="raw"),
        deepdiff_args=dict(required=False, type="list", default=[]),
        deepdiff_kwargs=dict(required=False, type="dict", default={})
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    result = {}
    ddiff = {}

    if HAS_DEEPDIFF:
        ddiff = DeepDiff(module.params['reference'], module.params["config"], *module.params["deepdiff_args"], **module.params["deepdiff_kwargs"]).to_dict()
    else:
        module.fail_json(msg="DeepDiff not installed on ansible controller. Please install it using 'pip install deepdiff'")

    if module._diff: # ansible --diff mode
        result.update({"diff": {"after": module.params["config"], "before": module.params['reference']}})

    result.update({
        "changed": True if ddiff else False,
        "deepdiff": ddiff
        })

    module.exit_json(**result)


if __name__ == "__main__":
    main()
