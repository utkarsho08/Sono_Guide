"""
Python version validator for the bootstrap launcher.
"""

from __future__ import annotations

import sys


def check_python_version() -> None:
    """Ensure the running Python interpreter meets the minimum requirements (>= 3.10)."""
    required = (3, 10)
    current = sys.version_info[:2]
    if current < required:
        print(
            f"[ERROR] Unsupported Python version: {sys.version.split()[0]}. "
            f"Sono-Guide requires Python {required[0]}.{required[1]} or higher.",
            file=sys.stderr,
        )
        sys.exit(1)
base_path = sys.executable
