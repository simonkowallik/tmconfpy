# -*- coding: utf-8 -*-
"""Command Line Interface for tmconfpy."""

import argparse
import sys

from . import __description__, __homepage__, __license__, __projectname__, __version__
from .parser import Parser


def _cli_arg_parser():
    """Build cli argument parser and return args object."""
    parser = argparse.ArgumentParser(
        prog=__projectname__,
        description=__description__,
        epilog=f"LICENSE: {__license__}, homepage: {__homepage__}",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=argparse.FileType("w"),
        help="File to write JSON output to.",
        nargs="?",
        default=sys.stdout,
    )
    parser.add_argument(
        "--format",
        type=str,
        help="Output format. Defaults to object.",
        choices=["object", "tabular", "jsonl"],
        default="object",
        required=False,
    )
    parser.add_argument(
        "file_path",
        type=argparse.FileType("r"),
        help="Path to tmconf file to read. Use - for STDIN.",
        nargs="?",
        default=(None if sys.stdin.isatty() else sys.stdin),
    )

    return parser.parse_args()


def cli():
    """Handle CLI interaction."""
    args = _cli_arg_parser()

    tmconf_content = args.file_path.read() if args.file_path is not None else ""

    if tmconf_content.strip() == "":
        print(
            "No file_path given or input is empty. Use -h|--help for help.",
            file=sys.stderr,
        )
        sys.exit(1)

    parsed = Parser(tmconf_content)

    if args.format == "tabular":
        args.output.write(parsed.tabular_json)
    elif args.format == "jsonl":
        args.output.write(parsed.jsonl)
    else:
        args.output.write(parsed.json)
