# tmconfpy - Ansible collection

## Purpose

tmconfpy as well as the tmconfpy ansible collection aim to make BIG-IP configurations more accessible by serializing the tmconf format to python data structures.

For more details about the relevant configuration files, data formats, tmconfpy and its ansible collection please have a look in the [documentation](https://simonkowallik.github.io/tmconfpy/).

## Installation

You can install the tmconfpy ansible collection either from [Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/simonkowallik/tmconfpy/) or from [GitHub](http://github.com/simonkowallik/tmconfpy).

```shell
ansible-galaxy collection install simonkowallik.tmconfpy

ansible-galaxy collection install git@github.com:simonkowallik/tmconfpy.git#ansible_collections/simonkowallik/tmconfpy,main
```

In your `requirements.yml` file you can use both ways as well:

```yaml
---
- name: simonkowallik/tmconfpy
  type: galaxy
  version: ">=1.1.0"

#- source: https://github.com/simonkowallik/tmconfpy.git#ansible_collections/simonkowallik/tmconfpy
#  type: git
#  version: main
```

## Example Playbooks

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
        msg: |+
          # This playbook requires the following:
          # requirements.yml
          collections:
          # https://galaxy.ansible.com/ui/repo/published/f5networks/f5_bigip/
          - name: f5networks.f5_bigip
            type: galaxy
            version: >=3.0.0
          # https://galaxy.ansible.com/ui/repo/published/simonkowallik/tmconfpy/
          - name: simonkowallik/tmconfpy
            type: galaxy
            version: >=1.1.0

    - name: "Fetch {{ bigip_configfile }}"
      simonkowallik.tmconfpy.tmconf_get:
        configfile: "{{ bigip_configfile }}"
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
```

```yaml
---
- name: "tmconfpy example playbook for auditing configuration"
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
    bigip_configfile: /config/bigip.conf

  tasks:
    - name: "Requirements Note"
      ansible.builtin.debug:
        msg: |+
          # This playbook requires the following:
          # requirements.yml
          collections:
          # https://galaxy.ansible.com/ui/repo/published/f5networks/f5_bigip/
          - name: f5networks.f5_bigip
            type: galaxy
            version: >=3.0.0
          # https://galaxy.ansible.com/ui/repo/published/simonkowallik/tmconfpy/
          - name: simonkowallik/tmconfpy
            type: galaxy
            version: >=1.1.0

    - name: "Set reference configuration"
      ansible.builtin.set_fact:
        #reference_config: "{{ lookup('file', './reference.json') | from_json }}"
        #reference_config: "{{ lookup('file', './reference.yaml') | from_yaml }}"
        reference_config:
        - name: clientssl-insecure-compatible
          object:
            cert: /Common/default.crt
            cert-key-chain:
              default:
                cert: /Common/default.crt
                chain: none
                key: /Common/default.key
                passphrase: none
            chain: none
            ciphers: ALL:!DH:!ADH:!EDH:@SPEED
            defaults-from: /Common/clientssl
            inherit-certkeychain: "true"
            key: /Common/default.key
            passphrase: none
            renegotiation: enabled
            secure-renegotiation: request
        - name: clientssl-secure-tls13
          object:
            app-service: none
            cert: /Common/default.crt
            cert-key-chain:
              default:
                cert: /Common/default.crt
                key: /Common/default.key
            chain: none
            ciphers: ecdhe:rsa:!sslv3:!rc4:!exp:!des
            defaults-from: /Common/clientssl
            inherit-certkeychain: "true"
            key: /Common/default.key
            options:
              - no-ssl
              - no-tlsv1
              - no-tlsv1.3
            passphrase: none
            renegotiation: disabled

    - name: "Fetch {{ bigip_configfile }}"
      simonkowallik.tmconfpy.tmconf_get:
        configfile: "{{ bigip_configfile }}"
      register: bigip_conf

    - name: "Extract relevant configuration"
      ansible.builtin.set_fact:
        # Using tmconf_tabular_kv to get a more structured output that is easier to query
        clientssl_config: "{{ bigip_conf.tmconf_tabular_kv | community.general.json_query(clientssl_query) }}"
        sys_autocheck_config: "{{ bigip_conf.tmconf_tabular_kv | community.general.json_query(sys_autocheck_query) }}"
      vars:
        clientssl_query: "[?path=='ltm profile client-ssl'].{name: name, object: object}"
        sys_autocheck_query: "[?path=='sys software'].{name: name, object: object}[?name=='update'].object.\"auto-check\""

    # Does not work particularly well
    #- name: "Compare configuration to reference configuration"
    #  ansible.utils.fact_diff:
    #    before: "{{ reference_config }}"
    #    after: "{{ clientssl_config }}"

    - name: "Compare clientssl configuration to reference using tmconf_diff"
      simonkowallik.tmconfpy.tmconf_diff:
        config: "{{ clientssl_config }}"
        reference: "{{ reference_config }}"
        # ignore order of lists and dicts, be verbose about changes, see: https://zepworks.com/deepdiff/current/basics.html
        deepdiff_kwargs: {"ignore_order": true, "verbose_level": 2}
      #failed_when: tmconf_diff_result.changed  # force failure if configuration deviates from reference
      register: tmconf_diff_result

    - name: "Print tmconf_diff result"
      ansible.builtin.debug:
        msg: "{{ tmconf_diff_result }}"

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
        msg: "{{ tmconf_diff_result }}"
```
