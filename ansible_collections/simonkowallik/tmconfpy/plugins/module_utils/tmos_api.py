#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import base64
import gzip
import io
import hashlib

from ansible.module_utils._text import to_text
from ansible.module_utils.connection import Connection


class APIClient:
    """Class to interact with the BIG-IP TMOS API."""

    def __init__(self, module):
        """Initialize the TMConfAPI class."""
        self.module = module
        self.connection = Connection(module._socket_path)

    def get(self, configfile):
        """GET configfile from BIG-IP TMOS using the API via f5networks.f5_bigip httpapi connection."""
        if configfile is None:
            raise ValueError("path value must be provided")

        response = self.connection.send_request(
            method="POST",
            path="/mgmt/tm/util/bash",
            headers={"Content-Type": "application/json"},
            payload=self._build_api_payload(configfile),
        )
        return response.get("contents", {}).get("commandResult")

    @staticmethod
    def _build_api_payload(configfile):
        return {
            "command": "run",
            "utilCmdArgs": f"-c 'test -f {configfile} || echo NOT_A_FILE;sha256sum --tag {configfile};cat {configfile} |gzip|base64 -w0'",
        }


class APIResultProcessor:
    """Class to process the result of the TMOS API response."""

    def __init__(self, module, commandResult):
        """
        Initialize the ApiResultProcessor class.
        Args:
            module (AnsibleModule): The AnsibleModule instance.
            commandResult (str): The commandResult from the TMOS API response.
        """
        self.commandResult = commandResult
        self.module = module

    @staticmethod
    def _decode_gzip_base64(gzip_base64):
        """Decode a base64 encoded gzipped string and return the decoded string."""
        decoded = base64.b64decode(gzip_base64)
        with gzip.GzipFile(fileobj=io.BytesIO(decoded)) as f:
            decoded = f.read()
        return decoded.decode("utf-8")

    @staticmethod
    def _generate_sha256sum(data):
        """Generate sha256sum (hex digest) of data."""
        m = hashlib.sha256()
        m.update(data.encode("utf-8"))
        return m.hexdigest()

    @property
    def result(self):
        """Process the commandResult, extracts and validates the tmconf text."""
        tmconf_text = None

        # "SHA256 (/config/bigip.conf) = 800c76d0e60451144f4a99ad1312b2a3163f57940b586880f2a458db7d3e9f8f\gzip_base64..."
        try:
            sha256sum, gzip_base64 = self.commandResult.split("\n")
            sha256sum = sha256sum.split(" ")[-1]
        except (IndexError, AttributeError, ValueError) as exc:
            self.module.fail_json(
                msg="Failed to process API response.",
                error_details=f"Could not parse the response data. Incorrect format. Exception details:{to_text(exc)}",
            )

        tmconf_text = self._decode_gzip_base64(gzip_base64)
        calculated_sha256sum = self._generate_sha256sum(tmconf_text)

        if not sha256sum == calculated_sha256sum:
            self.module.fail_json(
                msg="Failed to process API response.",
                error_details=f"Failed to verify the configfile. sha256sum of configfile ({sha256sum}) differs from the calculated sha256 checksum ({calculated_sha256sum}).",
            )

        return tmconf_text
