#!/usr/bin/env python3
import os
import sys


if __name__ == "__main__":
    print("INFO: validate_dashboard_v3_queries.py is deprecated; use validate_dashboard_queries.py")
    os.execvp("python3", ["python3", "scripts/validate_dashboard_queries.py", *sys.argv[1:]])