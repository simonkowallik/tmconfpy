# tmconfpy - Ansible collection

## Purpose

tmconfpy as well as the tmconfpy ansible collection aim to make BIG-IP configurations more accessible by serializing the tmconf format to python data structures.

For more details about the relevant configuration files, data formats, tmconfpy and its ansible collection please have a look in [CONFIG-FORMATS.md](https://github.com/simonkowallik/tmconfpy/blob/main/CONFIG-FORMATS.md).

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
  version: 1.0.0

#- source: https://github.com/simonkowallik/tmconfpy.git#ansible_collections/simonkowallik/tmconfpy
#  type: git
#  version: main
```

## Example Playbook

Please have a look at this [https://github.com/simonkowallik/tmconfpy/blob/main/ansible_collections/simonkowallik/tmconfpy/playbook/example-playbook.yml](example-playbook.yml).
