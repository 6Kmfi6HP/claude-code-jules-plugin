#!/usr/bin/env python3
"""jules_client.py — Alias for jules_cli.py.

This file exists for compatibility. All logic lives in jules_cli.py.
"""
import os
import sys

# Re-exec jules_cli.py with the same arguments
cli_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jules_cli.py")
os.execv(sys.executable, [sys.executable, cli_path] + sys.argv[1:])
