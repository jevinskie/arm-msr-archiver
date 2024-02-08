#!/usr/bin/env python3

import argparse
import logging
import sys
from typing import Final

from packaging.version import Version
from rich.console import Console
from rich.logging import RichHandler

from .. import _version, url_checker, url_generator

LOG_FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.WARNING,
    format=LOG_FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(console=Console(stderr=True), rich_tracebacks=True)],
)

program_name = "arm-mra-archiver-live-urls"

log = logging.getLogger(program_name)


def get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=program_name)
    parser.add_argument("-v", "--verbose", action="store_true", help="be verbose")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s version: {Version(_version.version)}",
    )
    return parser


def real_main(args: argparse.Namespace) -> int:
    verbose: Final[bool] = args.verbose
    if verbose:
        log.setLevel(logging.INFO)
        log.info(f"{program_name}: verbose mode enabled")
    possible_url_bundles = url_generator.generate_url_bundles()
    live_url_bundles = url_checker.get_live_urls(possible_url_bundles)
    for url_bundle in live_url_bundles:
        print(f"URL bundle:\n{url_bundle}\n")
    return 0


def main() -> int:
    try:
        args = get_arg_parser().parse_args()
        return real_main(args)
    except Exception:
        log.exception(f"Received an unexpected exception when running {program_name}")
        return 1
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
