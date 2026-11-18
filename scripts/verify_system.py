#!/usr/bin/env python3
"""Verify the deployed inventory API and its database connection."""

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


def fetch(base_url, path, timeout):
    url = urljoin(f"{base_url.rstrip('/')}/", path.lstrip('/'))
    request = Request(url, headers={"Accept": "application/json"})

    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except HTTPError as error:
        return error.code, error.read()
    except URLError as error:
        raise RuntimeError(str(error.reason)) from error


def print_result(passed, check, detail):
    label = "PASS" if passed else "FAIL"
    print(f"{label} {check}: {detail}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=os.environ.get("INVENTORY_API_URL", "http://localhost:8000"),
        help="API base URL (default: %(default)s)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="request timeout in seconds (default: %(default)s)",
    )
    args = parser.parse_args()

    results = []
    health_payload = {}

    try:
        health_status, health_body = fetch(args.base_url, "/health/", args.timeout)
        try:
            health_payload = json.loads(health_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            health_payload = {}

        health_ok = (
            health_status == 200 and health_payload.get("status") == "healthy"
        )
        health_detail = (
            "HTTP 200 and healthy status"
            if health_ok
            else f"HTTP {health_status} or invalid health response"
        )
    except RuntimeError as error:
        health_ok = False
        health_detail = f"request failed ({error})"

    results.append(health_ok)
    print_result(health_ok, "Health endpoint", health_detail)

    try:
        api_status, _ = fetch(args.base_url, "/api/products/", args.timeout)
        api_ok = api_status in {200, 401, 403}
        api_detail = (
            f"HTTP {api_status}; API route is reachable"
            if api_ok
            else f"unexpected HTTP {api_status}"
        )
    except RuntimeError as error:
        api_ok = False
        api_detail = f"request failed ({error})"

    results.append(api_ok)
    print_result(api_ok, "API availability", api_detail)

    database_ok = health_ok and health_payload.get("database") == "connected"
    database_detail = (
        "health endpoint reports connected"
        if database_ok
        else "health endpoint does not report a connected database"
    )
    results.append(database_ok)
    print_result(database_ok, "Database connectivity", database_detail)

    if all(results):
        print("PASS System verification completed successfully")
        return 0

    print("FAIL System verification detected one or more problems")
    return 1


if __name__ == "__main__":
    sys.exit(main())
