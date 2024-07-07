# -*- coding: utf-8 -*-
"""tmconfpy - Serialize F5 BIG-IP tmconf files to dict/JSON."""

import json
import logging
import sys
import re
from collections import namedtuple
from typing import Dict, Optional

# pylint: disable=line-too-long,too-many-branches

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.INFO,
    stream=sys.stderr,
)
log = logging.getLogger(__name__)
#handler = logging.StreamHandler(sys.stderr)
#handler.setLevel(logging.INFO)
#log.addHandler(handler)

# namedtuple for tabular data
tabularTmconf = namedtuple("tabularTmconf", ["path", "name", "object"])


class Parser:
    """Parse tmconf data or file and serialize it to a python dict or JSON (str)."""

    def __init__(self, tmconf: str, is_filepath: bool = False):
        '''
        Parse tmconf data or file and serialize it to a python dict and JSON.

        Args:
            tmconf (str): tmconf data (str) or file path.
            is_filepath (bool): If True, `tmconf` is a file path, otherwise it is tmconf data.

        Example:
            >>> from tmconfpy import Parser
            >>> parsed = Parser('example/imap.tmconf', is_filepath=True)
            >>> parsed.dict
            {'ltm profile imap imap': {'activation-mode': 'require'}}
            >>> tmconf = r"""
            ... ltm profile pop3 pop3 {
            ...     activation-mode require
            ... }
            ... ltm profile imap imap {
            ...     activation-mode require
            ... }
            ... """
            >>> parsed = Parser(tmconf)
            >>> parsed.json
            '{"ltm profile pop3 pop3": {"activation-mode": "require"}, "ltm profile imap imap": {"activation-mode": "require"}}'
            >>> parsed.tabular
            [tabularTmconf(path='ltm profile pop3', name='pop3', object={'activation-mode': 'require'}), tabularTmconf(path='ltm profile imap', name='imap', object={'activation-mode': 'require'})]
            >>> parsed.tabular_json
            '[["ltm profile pop3", "pop3", {"activation-mode": "require"}], ["ltm profile imap", "imap", {"activation-mode": "require"}]]'
            >>> parsed.jsonl
            '{"path": "ltm profile pop3", "name": "pop3", "object": {"activation-mode": "require"}}\n{"path": "ltm profile imap", "name": "imap", "object": {"activation-mode": "require"}}'
        '''
        self._tmconf_text = self._read_tmconf_file(tmconf) if is_filepath else tmconf

        self._tmconf_dict = self._parse_tmconf_content()
        self._tmconf_json = ""
        self._tmconf_jsonl = ""
        self._tmconf_tabular: list[tabularTmconf] = []
        self._tmconf_tabular_json = ""

    @property
    def dict(self) -> dict:
        """Parsed tmconf as python dictionary."""
        return self._tmconf_dict

    @property
    def json(self) -> str:
        """Parsed tmconf as JSON string."""
        if not self._tmconf_json:
            self._tmconf_json = json.dumps(self._tmconf_dict)
        return self._tmconf_json

    @property
    def jsonl(self) -> str:
        """Parsed tmconf as JSONL string."""
        if not self._tmconf_jsonl:
            jsonl = [
                json.dumps(path_name_object._asdict())
                for path_name_object in self.tabular
            ]
            self._tmconf_jsonl = "\n".join(jsonl)
        return self._tmconf_jsonl

    @property
    def tabular_json(self) -> str:
        """Parsed tmconf as JSON array of arrays, each with three fields, path (str), name (str) object (object)."""
        if not self._tmconf_tabular_json:
            self._tmconf_tabular_json = json.dumps(
                [path_name_object for path_name_object in self.tabular]
            )
        return self._tmconf_tabular_json

    @property
    def tabular(self) -> list[tabularTmconf]:
        """Parsed tmconf as list of tuples, each with three fields, path (str), name (str) object (dict)."""
        if not self._tmconf_tabular:
            self._tmconf_tabular = [
                (lambda path, obj: tabularTmconf(" ".join(path[:-1]), path[-1], obj))(
                    item[0].split(" "), item[1]
                )
                for item in self.dict.items()
            ]
        return self._tmconf_tabular

    def _group_objects(self, arr) -> list:
        """Group tmconf objects into a list."""
        group = []
        i = 0
        while i < len(arr):
            current_line = arr[i]

            if "{" in current_line and "}" in current_line and current_line[0] != " ":
                group.append([current_line])
            elif current_line.strip().endswith("{") and not current_line.startswith(
                " "
            ):
                c = 0
                rule_flag = self._is_irule(current_line)

                bracket_count = 1
                while bracket_count != 0:
                    c += 1
                    line = arr[i + c]
                    subcount = 0

                    previous_char = ""
                    if not (
                        (
                            line.strip().startswith("#")
                            or line.strip().startswith("set")
                            or line.strip().startswith("STREAM")
                        )
                        and rule_flag
                    ):
                        updated_line = (
                            line.strip().replace('\\"', "").replace(r'".+"', "")
                        )
                        for char in updated_line:
                            if char == "{" and previous_char != "\\":
                                subcount += 1
                            if char == "}" and previous_char != "\\":
                                subcount -= 1
                            previous_char = char

                        if self._is_irule(line):
                            c -= 1
                            bracket_count = 0
                        bracket_count += subcount

                group.append(arr[i : i + c + 1])
                i += c
            i += 1
        return group

    def _orchestrate(self, arr):
        """Orchestrate the parsing of tmconf objects."""
        key = self._get_object_name(arr[0])

        # remove opening and closing brackets which are at the first and last position
        arr.pop()

        if len(arr) >= 1:
            arr.pop(0)

        obj = {}

        # case: iRules (multiline string)
        if self._is_irule(key):
            obj = "\n".join(arr)

        # case: monitor min X of {...}
        elif "monitor min" in key:
            arr = [s.strip() for s in arr]
            obj = " ".join(arr).split(" ")

        # skip cli script, also skip 'sys crypto cert-order-manager', it has quotation marks around curly brackets of 'order-info'
        elif "cli script" not in key and "sys crypto cert-order-manager" not in key:
            i = 0
            while i < len(arr):
                # case: nested object
                # quoted bracket "{" won't trigger recursion
                if arr[i].endswith("{") and len(arr) != 1:
                    c = 0
                    while arr[i + c] != "    }":
                        c += 1
                        if (i + c) >= len(arr):
                            raise ValueError(
                                f"Missing or mis-indented '}}' for line number {i+1}: '{arr[i]}'"
                            )
                    sub_obj_arr = self._remove_indent(arr[i : i + c + 1])

                    # coerce unnamed objects into array
                    coerce_arr = []
                    arr_idx = 0
                    for line in sub_obj_arr:
                        if line == "    {":
                            line = line.replace("{", f"{arr_idx} {{")
                            arr_idx += 1
                        coerce_arr.append(line)

                    # recurse nested object
                    obj.update(self._orchestrate(coerce_arr))

                    # skip over nested block
                    i += c

                # case: empty object
                elif "".join(arr[i].split(" ")).endswith("{ }") or "".join(
                    arr[i].split(" ")
                ).endswith("{}"):
                    obj[arr[i].split("{")[0].strip()] = {}

                # case: pseudo-array pattern (coerce to array)
                elif "{" in arr[i] and "}" in arr[i] and '"' not in arr[i]:
                    obj_name = arr[i].split("{")[0].strip()
                    obj[obj_name] = self._obj_to_arr(arr[i])

                # case: single-string property
                elif (
                    " " not in arr[i].strip()
                    or re.match(r'^"[\s\S]*"$', arr[i].strip())
                ) and "}" not in arr[i]:
                    obj[arr[i].strip()] = ""

                # regular string property
                # ensure string props on same indentation level
                elif self._count_indent(arr[i]) == 4:
                    # case: multiline string
                    count = arr[i].count('"')
                    if count % 2 == 1:
                        c = 1

                        # keep count of '"'?
                        while arr[i + c] and arr[i + c].count('"') % 2 != 1:
                            c += 1

                        chunk = arr[i : i + c + 1]
                        sub_obj_arr = self._arr_to_multiline_str(chunk)
                        obj.update(sub_obj_arr)
                        i += c

                    # case: typical string
                    else:
                        tmp = self._str_to_obj(arr[i].strip())
                        # case: gtm monitor external and user-defined property
                        if (
                            key.startswith("gtm monitor external")
                            and "user-defined" in tmp
                        ):
                            if "user-defined" not in obj:
                                obj["user-defined"] = {}
                            tmp_obj = self._str_to_obj(tmp["user-defined"])
                            obj["user-defined"][list(tmp_obj.keys())[0]] = list(
                                tmp_obj.values()
                            )[0]
                        else:
                            obj.update(tmp)

                # else log exception
                else:
                    log.warning("UNRECOGNIZED LINE for object '%s': '%s'", key, arr[i])
                i += 1

        return {key: obj}

    @staticmethod
    def _read_tmconf_file(filepath: str) -> str:
        """read tmconf file, perform sanitization and checks, then return content as str."""
        with open(filepath, "rb") as file:
            data = file.read().decode()

        # silent dos2unix
        data = data.replace("\r\n", "\n")
        # log warning of data contains utf-8 characters
        if not data.isascii():
            log.warning("File '%s' contains non-ASCII characters.", filepath)
        return data

    def _parse_tmconf_content(self) -> Dict:
        """Parse the text of a tmconf file and return a dictionary of objects."""
        file_arr = self._tmconf_text.split("\n")

        # gtm topology
        new_file_arr: list = []
        topology_arr: list = []
        topology_count = 0
        longest_match_enabled = True
        in_topology = False
        irule = 0
        data: Dict = {}

        for line in file_arr:
            # Process comments in iRules:
            if irule == 0:
                if line.strip().startswith("# "):
                    # mark comments outside of irules with specific prefix
                    line = line.strip().replace("# ", "#comment# ")
                elif self._is_irule(line):
                    irule += 1
            # don't count brackets in commented or special lines
            elif not line.strip().startswith("#"):
                irule = irule + line.count("{") - line.count("}")

            ldns = ""
            server = ""
            if "topology-longest-match" in line and "no" in line:
                longest_match_enabled = False
            if line.startswith("gtm topology ldns:"):
                in_topology = True
                if len(topology_arr) == 0:
                    topology_arr.append("gtm topology /Common/Shared/topology {")
                    topology_arr.append("    records {")
                ldns_index = line.index("ldns:")
                server_index = line.index("server:")
                bracket_index = line.index("{")
                ldns = line[ldns_index + 5 : server_index].strip()
                topology_arr.append(f"        topology_{topology_count} {{")
                topology_count += 1
                topology_arr.append(f"            source {ldns}")
                server = line[server_index + 7 : bracket_index].strip()
                topology_arr.append(f"            destination {server}")
            elif in_topology:
                if line == "}":
                    in_topology = False
                    topology_arr.append("        }")
                else:
                    topology_arr.append(f"        {line}")
            else:
                new_file_arr.append(line)

        if topology_arr:
            topology_arr.append(
                f"        longest-match-enabled {'yes' if longest_match_enabled else 'no'}"
            )
            topology_arr.append("    }")
            topology_arr.append("}")

        file_arr = new_file_arr + topology_arr

        # remove whitespace and comments
        file_arr = [
            line
            for line in file_arr
            if not (line == "" or line.strip().startswith("#comment# "))
        ]
        group_arr = [self._orchestrate(obj) for obj in self._group_objects(file_arr)]
        group_arr_dict = self._arr_to_dict(group_arr)

        return {**data, **group_arr_dict}

    @staticmethod
    def _get_object_name(string: str) -> str:
        """Returns the full object name."""
        return string.rstrip().rstrip("{}").rstrip("{ }").strip()

    @staticmethod
    def _is_irule(string: str) -> bool:
        """Returns True if `string` is an iRule, False otherwise."""
        return "ltm rule" in string or "gtm rule" in string or "pem irule" in string

    @staticmethod
    def _count_indent(string: str) -> Optional[int]:
        """Count the number of whitespaces at the beginning of a string."""
        return re.search(r"\S", string).start() if re.search(r"\S", string) else None

    def _remove_indent(self, arr) -> list:
        """Remove indent (4 whitespaces) from each line in a list of strings if the line is indented."""
        return [line[4:] if self._count_indent(line) > 1 else line for line in arr]

    @staticmethod
    def _obj_to_arr(line) -> list:
        """Convert an tmconf object to an array."""
        split = line.split("{")
        body = "".join(split[1].split("}")).strip()
        return body.split(" ")

    @staticmethod
    def _str_to_obj(line) -> Dict:
        """Convert a tmconf string to a dictionary."""
        split = line.strip().split(" ")
        key = split.pop(0)
        return {key: " ".join(split)}

    @staticmethod
    def _arr_to_multiline_str(arr) -> Dict:
        """Convert an array to a multiline string."""
        split = arr[0].strip().split(" ")
        key = split.pop(0)
        arr[0] = " ".join(split)
        return {key: "\n".join(arr)}

    @staticmethod
    def _arr_to_dict(arr) -> Dict:
        """Convert an array of objects to a dictionary."""
        _data = {}
        for obj in arr:
            _data.update(obj)
        return _data
