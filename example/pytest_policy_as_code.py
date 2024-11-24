#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Example: Using pytest to implement policy-as-code / audit configuration is compliant with standards.
"""


import pytest

from tmconfpy import Parser

# bigip.conf file in the local directory
bigip_conf = Parser("bigip.conf", is_filepath=True)

class Test_audit_virtuals:
    """
    Test suite for virtual server configuration compliance.
    """

    # extract all virtual server configurations
    CONFIG_DATA = [
        conf for conf in bigip_conf.tabular_kv if conf.get("path") == "ltm virtual"
    ]

    @pytest.mark.parametrize(
        "destination, profile, match",
        [
            (":443", "/Common/websecurity", "exact"),
            (":443", "/Common/clientssl", "startswith"),
            (":443", "/Common/serverssl", "startswith"),
        ],
    )
    def test_for_mandatory_profiles(self, destination, profile, match):
        """
        Test that virtual servers have mandatory profiles attached
        
        Goals:
        - Ensure all virtual servers offering :443 have a WAF policy attached (checking for /Common/websecurity)
        - Ensure all virtual servers offering :443 have a clientssl profile attached (checking for /Common/clientssl*)
        - Ensure all virtual servers offering :443 have a serverssl profile attached (checking for /Common/serverssl*)
        """
        for service in self.CONFIG_DATA:
            if destination in service["object"]["destination"]:
                if match == "exact":
                    assert (
                        profile in service["object"]["profiles"]
                    ), f"Service {service['name']} with {destination} destination missing {profile} profile"
                elif match == "startswith":
                    assert any(
                        key.startswith(profile) for key in service["object"]["profiles"]
                    ), f"Service {service['name']} with {destination} destination missing {profile} profile"

    @pytest.mark.parametrize(
        "destination, attribute",
        [(":80", "pool")],
    )
    def test_absence_of_pool_on_http_virtuals(self, destination, attribute):
        """
        Test that virtual servers with :80 destination do not have a pool set, redirect only!
        """
        for service in self.CONFIG_DATA:
            if destination in service["object"]["destination"]:
                assert (
                    service["object"].get(attribute) is None
                ), f"Service {service['name']} with {destination} destination should not have attribute {attribute}"

    @pytest.mark.parametrize(
        "destination, rule",
        [(":80", "/Common/redirect_to_https")],
    )
    def test_redirect_rule_on_http_virtuals(self, destination, rule):
        """
        Test that all virtual servers with :80 destination have a standardized redirect rule attached.
        """
        for service in self.CONFIG_DATA:
            if destination in service["object"]["destination"]:
                assert (
                    "rules" in service["object"]
                    and service["object"]["rules"] == {rule: ""}
                ), f"Service {service['name']} with {destination} destination missing {rule} rule"

    def test_allowed_virtual_server_ports(self, allowed_ports=["80", "443"]):
        """
        Test that all virtual servers are only listening on allowed ports.
        """
        for service in self.CONFIG_DATA:
            service_port = service["object"]["destination"].split("%")[0].split(":")[1]
            assert (
                service_port in allowed_ports
            ), f"Service {service['name']} listening on non-allowed port: {service_port}"

class Test_audit_clientssl:
    """
    Test suite for clientssl profile configuration compliance.
    """

    # extract all clientssl profile configurations
    CONFIG_DATA = [
        conf for conf in bigip_conf.tabular_kv if conf.get("path") == "ltm profile client-ssl"
    ]

    def test_chain_is_set(self):
        """
        Test that clientssl profiles have a CA chain set.
        """
        for service in self.CONFIG_DATA:
            assert service["object"].get("chain"), f"Service {service['name']} missing CA chain"
            for ckc in service["object"].get("cert-key-chain", {}).values():
                assert ckc.get("chain"), f"Service {service['name']} missing CA chain in cert-key-chain"

    def test_defaults_from_secure(self):
        """
        Test that clientssl profiles inherit from the secure clientssl profile templates.
        """
        for service in self.CONFIG_DATA:
            parent = service["object"].get("defaults-from")
            assert (
                parent.startswith("/Common/clientssl-secure")
            ), f"Service {service['name']} should inherit from /Common/clientssl-secure* not {parent}"
