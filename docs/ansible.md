---
layout: default
title: Ansible
nav_enabled: true
nav_order: 3
---
# tmconfpy - Ansible collection

## Purpose

tmconfpy as well as the tmconfpy ansible collection aim to make BIG-IP configurations more accessible by serializing the tmconf format to python data structures.

This can be used to replace facts gathering in ansible, for ansible implementation specific purposes like checking for dependencies, or to query specific configuration information.

It also can help to audit configurations by comparing the "on-device" configuration with stored references.

***NOTE:*** As the module copies configuration files from F5 BIG-IP devices, those configurations might contain sensitive data. Make sure YOU, as the implementor, *ensure* data security!

For more details about the relevant configuration files, data formats, tmconfpy and its ansible collection please have a look in the [documentation](https://simonkowallik.github.io/tmconfpy/).

## Installation

You can install the tmconfpy ansible collection either from [](Ansible Galaxy) or from github.

```shell
ansible-galaxy collection install simonkowallik.tmconfpy

ansible-galaxy collection install git@github.com:simonkowallik/tmconfpy.git#ansible_collections/simonkowallik/tmconfpy,main
```

In your `requirements.yml` file you can use both ways as well:

```yaml
---
- name: simonkowallik/tmconfpy
  type: galaxy
  version: 1.1.0

#- source: https://github.com/simonkowallik/tmconfpy.git#ansible_collections/simonkowallik/tmconfpy
#  type: git
#  version: main
```

## Example Playbook

```yaml
---
- name: "tmconfpy example playbook"
  hosts: all
  connection: httpapi
  gather_facts: false

  vars:
    provider:
      server: 192.0.2.245
      server_port: 443
      user: admin
      password: admin  # use vault!
      validate_certs: yes
    # map provider variables to collection v2 variables
    ansible_host: "{{ provider.server }}"
    ansible_user: "{{ provider.user }}"
    ansible_httpapi_password: "{{ provider.password }}"
    ansible_httpapi_port: "{{ provider.server_port }}"
    ansible_network_os: f5networks.f5_bigip.bigip
    ansible_httpapi_use_ssl: yes
    ansible_httpapi_validate_certs: "{{ provider.validate_certs }}"
    # the above is typically defined in a group_vars and host_vars and ansible-vault
    # path to the configuration file on the BIG-IP
    bigip_configfile: /config/bigip_user.conf

  tasks:
    - name: "Requirements Note"
      ansible.builtin.debug:
        msg: |
          # This playbook requires the following:
          # requirements.yml
          collections:
          # https://galaxy.ansible.com/ui/repo/published/f5networks/f5_bigip/
          - name: f5networks.f5_bigip
            type: galaxy
            version: ">=3.0.0"
          # https://galaxy.ansible.com/ui/repo/published/simonkowallik/tmconfpy/
          - name: simonkowallik/tmconfpy
            type: galaxy
            version: ">=1.1.0"

    - name: "Fetch {{ bigip_configfile }} in tabular format"
      simonkowallik.tmconfpy.tmconf_get:
        configfile: "{{ bigip_configfile }}"
        format: tabular
      register: tabular_config

    # tabular format has 3 columns, object_path, object_name and the object itself.
    # each entry in the tmconf file is a row.
    - name: "Print {{ bigip_configfile }} in tabular format"
      ansible.builtin.debug:
        var: tabular_config.tmconf_tabular

    # object format uses keys that represent the object_path and object_name. The value is the object itself.
    - name: "Fetch {{ bigip_configfile }} in object format (default)"
      simonkowallik.tmconfpy.tmconf_get:
        configfile: "{{ bigip_configfile }}"
      register: config

    - name: "Print {{ bigip_configfile }} in object format (default)"
      ansible.builtin.debug:
        var: config.tmconf

    - name: "Save tmconf to JSON file"
      ansible.builtin.copy:
        content: "{{ config.tmconf | to_nice_json }}"
        dest: "./{{ bigip_configfile }}"

```
