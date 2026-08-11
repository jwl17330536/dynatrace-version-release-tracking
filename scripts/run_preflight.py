#!/usr/bin/env python3
"""Canonical preflight entrypoint.

This wrapper preserves backward compatibility with `run_v5_preflight.py`
while giving contributors a version-agnostic command surface.
"""

from run_v5_preflight import main


if __name__ == "__main__":
    raise SystemExit(main())
