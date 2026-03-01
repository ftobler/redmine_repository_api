#!/usr/bin/env python3
"""Wait for Redmine to become available."""

import sys
import time
import urllib.request
import urllib.error

URL = "http://localhost/"
ATTEMPTS = 36
INTERVAL = 5


def wait():
    for i in range(1, ATTEMPTS + 1):
        try:
            urllib.request.urlopen(URL, timeout=5)
            print("Redmine is up!")
            return
        except (urllib.error.URLError, OSError):
            print(f"Attempt {i}/{ATTEMPTS}, sleeping {INTERVAL}s...")
            time.sleep(INTERVAL)

    print("Redmine did not become ready in time.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    wait()
