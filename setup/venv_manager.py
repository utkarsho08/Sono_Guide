"""
Virtual Environment Manager for locating and initializing the project's venv.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from setup.dependencies import PROJECT_ROOT, VENV_DIR


def get_venv_python() -> Path:
    """Get the platform-independent path to the virtual environment python interpreter."""
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def locate_venv() -> bool:
    """Check if the virtual environment exists and is healthy."""
    return get_venv_python().is_file()


def create_venv() -> None:
    """Create the virtual environment if it does not exist."""
    if locate_venv():
        return

    print(f"[STATUS] Creating virtual environment in: {VENV_DIR}")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            cwd=PROJECT_ROOT,
            check=True,
        )
        print("[STATUS] Virtual environment created successfully.")
    except (subprocess.SubprocessError, OSError) as e:
        print(f"[ERROR] Failed to create virtual environment: {e}", file=sys.stderr)
        sys.exit(1)
