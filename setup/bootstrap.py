"""
Bootstrap helper module for model verification and application launching.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from setup.dependencies import PROJECT_ROOT


def verify_models() -> None:
    """Verify that the required model weights and demo video assets exist."""
    assets_dir = PROJECT_ROOT / "assets"
    model_path = assets_dir / "models" / "best.pt"
    video_path = assets_dir / "images" / "ultrasound_demo.mp4"

    missing = []
    if not model_path.is_file():
        missing.append(f"Model file missing: {model_path.relative_to(PROJECT_ROOT)}")
    if not video_path.is_file():
        missing.append(f"Demo video asset missing: {video_path.relative_to(PROJECT_ROOT)}")

    if missing:
        print("[ERROR] Missing critical assets or model files:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        print(
            "[ERROR] Please download the required model weights and place them in assets/models/ before starting.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("[STATUS] Model weights and demo assets verified successfully.")


def launch_application(venv_python: Path) -> int:
    """Launch the main application using the virtual environment interpreter."""
    print("[STATUS] Launching Sono-Guide application...")

    env = os.environ.copy()
    src_dir = str(PROJECT_ROOT / "src")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        src_dir if not existing_pythonpath else f"{src_dir}{os.pathsep}{existing_pythonpath}"
    )

    main_py = PROJECT_ROOT / "main.py"

    try:
        completed = subprocess.run([str(venv_python), str(main_py)], cwd=PROJECT_ROOT, env=env)
        return completed.returncode
    except Exception as e:
        print(f"[ERROR] Application crash or unexpected error: {e}", file=sys.stderr)
        return 1
