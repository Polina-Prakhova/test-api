#!/usr/bin/env python3
"""
Simple entry point to run the pytest-based API test suite.

Usage examples:
  - Run all tests with defaults:
      python run_all.py

  - Override API base URL (passed to tests via API_BASE_URL env var):
      python run_all.py --base-url http://localhost:8000

  - Filter tests with -k or -m (passed through to pytest):
      python run_all.py -k "auth and not slow" -m "not flaky"

  - Generate JUnit XML report:
      python run_all.py --junit-xml report.xml

Any extra arguments not recognized by this script are forwarded to pytest.
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List

import pytest


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run pytest API tests with optional configuration.",
        add_help=True,
    )
    parser.add_argument(
        "--base-url",
        dest="base_url",
        help="Base URL of the API under test (sets API_BASE_URL env var).",
        default=None,
    )
    parser.add_argument(
        "--path",
        dest="tests_path",
        help="Path to tests discovery root (default: tests).",
        default="tests",
    )
    parser.add_argument(
        "--maxfail",
        dest="maxfail",
        type=int,
        default=None,
        help="Exit after first N failures.",
    )
    parser.add_argument(
        "--junit-xml",
        dest="junit_xml",
        default=None,
        help="Create JUnit-XML style report file at given path.",
    )
    parser.add_argument(
        "-k",
        dest="keyword",
        default=None,
        help="Only run tests which match the given substring expression.",
    )
    parser.add_argument(
        "-m",
        dest="markers",
        default=None,
        help="Only run tests matching given markers expression.",
    )

    # Use parse_known_args to forward extra args directly to pytest
    args, remaining = parser.parse_known_args(argv)
    args._remaining = remaining  # type: ignore[attr-defined]
    return args


def main(argv: List[str]) -> int:
    args = parse_args(argv)

    if args.base_url:
        os.environ["API_BASE_URL"] = args.base_url

    pytest_args: List[str] = []

    # Show extra test summary info: skipped, failed, xfailed, xpassed, errors
    pytest_args.extend(["-rA"])  # report all except passes

    if args.maxfail is not None:
        pytest_args.extend(["--maxfail", str(args.maxfail)])

    if args.junit_xml:
        pytest_args.extend(["--junit-xml", args.junit_xml])

    if args.keyword:
        pytest_args.extend(["-k", args.keyword])

    if args.markers:
        pytest_args.extend(["-m", args.markers])

    # Add user-provided passthrough args at the end so they can override defaults
    if getattr(args, "_remaining", None):
        pytest_args.extend(args._remaining)  # type: ignore[arg-type]

    # Test discovery root
    pytest_args.append(args.tests_path)

    print("Running pytest with arguments:", " ".join(pytest_args))
    return pytest.main(pytest_args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
