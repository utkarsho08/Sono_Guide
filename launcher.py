#!/usr/bin/env python3
"""
Thin orchestration launcher for Sono-Guide.

Delegates version validation, virtual environment management, dependency manager
checks, and application bootstrapper stages to modular helper scripts in setup/.
"""

from __future__ import annotations

import argparse
import sys

try:
    from setup.bootstrap import launch_application, verify_models
    from setup.dependency_manager import install_dependencies, verify_dependencies
    from setup.python_checker import check_python_version
    from setup.venv_manager import create_venv, get_venv_python
except ImportError as e:
    print(f"[ERROR] Failed to import bootstrapper components: {e}", file=sys.stderr)
    print("[ERROR] Run this launcher from the project root directory.", file=sys.stderr)
    sys.exit(1)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the orchestrator."""
    parser = argparse.ArgumentParser(
        description="Bootstrap Sono-Guide dependencies and launch the application.",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip dependency installation and only run main.py with the venv interpreter.",
    )
    parser.add_argument(
        "--install-only",
        action="store_true",
        help="Install dependencies and exit without launching the application.",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Enable development mode (install development dependencies).",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show full stack trace on unexpected launcher failures.",
    )
    parser.add_argument(
        "--show-plan",
        action="store_true",
        help="Print the install stages and dependency groups, then exit.",
    )
    return parser.parse_args()


def print_install_plan() -> None:
    """Print the configured installation and execution plan."""
    print("Sono-Guide Installation & Execution Plan:")
    print("  1. Python Version Check (Requires Python >= 3.10)")
    print("  2. Virtual Environment Setup (Checks and creates .venv)")
    print("  3. Upgrade pip (python -m pip install --upgrade pip)")
    print("  4. Install CPU-only PyTorch (python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu)")
    print("  5. Install Ultralytics (python -m pip install ultralytics)")
    print("  6. Install Core Requirements (python -m pip install -r requirements.txt)")
    print("  7. (Optional --dev) Install Dev Requirements (python -m pip install -r requirements/dev.txt)")
    print("  8. Model Verification (Checks assets/models/best.pt and demo video)")
    print("  9. Application Launch (Runs main.py with .venv Python interpreter)")


def main() -> int:
    """Main orchestrator workflow entry point."""
    args = parse_args()

    if args.show_plan:
        print_install_plan()
        return 0

    try:
        # Step 1: Check Python version
        check_python_version()

        # Step 2: Locate/create virtual environment
        create_venv()
        venv_python = get_venv_python()

        # Step 3: Audit and install dependencies
        if not args.skip_install:
            missing_install, missing_dev = verify_dependencies(venv_python, dev_mode=args.dev)

            if missing_install or missing_dev:
                print("[STATUS] Missing dependencies detected. Commencing installation.")
                install_dependencies(venv_python, missing_install, missing_dev)
            else:
                print(
                    "[STATUS] All dependencies satisfied. Offline-friendly mode: skipping installations."
                )

        # Step 4: Verify models and assets
        verify_models()

        if args.install_only:
            print("[STATUS] Installation completed successfully. Exiting.")
            return 0

        # Step 5: Launch application
        return launch_application(venv_python)

    except Exception as e:
        print(f"[ERROR] An unexpected failure occurred: {e}", file=sys.stderr)
        if args.debug:
            import traceback

            traceback.print_exc()
        else:
            print("[ERROR] Run with '--debug' to see full error traceback.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
