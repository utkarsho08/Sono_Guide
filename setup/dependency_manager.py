"""
Dependency manager for package detection, verification, and installation.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from setup.dependencies import (
    DEVELOPMENT_DEPENDENCIES,
    HEAVY_AI_DEPENDENCIES,
    LIGHTWEIGHT_DEPENDENCIES,
    PACKAGE_IMPORT_NAMES,
    PROJECT_ROOT,
    PYTORCH_CPU_INDEX,
    REQUIREMENTS_DEV,
    REQUIREMENTS_LIGHTWEIGHT,
    TORCH_CPU_PACKAGES,
)


def is_package_installed(package_name: str, venv_python: Path) -> bool:
    """Check if a package is installed in the virtual environment.

    Tries import-based verification using metadata and specs.
    """
    dist_name = package_name.strip()
    script_metadata = (
        "import importlib.metadata, sys; "
        "try: "
        f"  importlib.metadata.version({dist_name!r}); "
        "  sys.exit(0); "
        "except importlib.metadata.PackageNotFoundError: "
        "  sys.exit(1);"
    )
    result = subprocess.run(
        [str(venv_python), "-c", script_metadata],
        cwd=PROJECT_ROOT,
        capture_output=True,
    )
    if result.returncode == 0:
        return True

    import_name = PACKAGE_IMPORT_NAMES.get(package_name, package_name.replace("-", "_"))
    script_import = (
        "import importlib.util, sys; "
        f"sys.exit(0 if importlib.util.find_spec({import_name!r}) else 1)"
    )
    result = subprocess.run(
        [str(venv_python), "-c", script_import],
        cwd=PROJECT_ROOT,
        capture_output=True,
    )
    return result.returncode == 0


def verify_dependencies(venv_python: Path, dev_mode: bool = False) -> tuple[list[str], list[str]]:
    """Verify which packages are missing in the virtual environment.

    Returns:
        tuple: (list_of_missing_core_and_ai, list_of_missing_dev)
    """
    missing_install = []
    missing_dev = []

    # 1. Check heavy AI dependencies (dynamic from setup.dependencies)
    for pkg in HEAVY_AI_DEPENDENCIES:
        if not is_package_installed(pkg, venv_python):
            missing_install.append(pkg)

    # 2. Check core dependencies (dynamic from setup.dependencies)
    for pkg in LIGHTWEIGHT_DEPENDENCIES:
        if pkg not in HEAVY_AI_DEPENDENCIES and pkg not in missing_install:
            if not is_package_installed(pkg, venv_python):
                missing_install.append(pkg)

    # 3. Check dev dependencies if dev_mode is active (dynamic from setup.dependencies)
    if dev_mode:
        for pkg in DEVELOPMENT_DEPENDENCIES:
            if not is_package_installed(pkg, venv_python):
                missing_dev.append(pkg)

    return missing_install, missing_dev


def run_pip_command(venv_python: Path, args: list[str]) -> None:
    """Execute a pip command in the virtual environment python interpreter."""
    cmd = [str(venv_python), "-m", "pip", *args]
    try:
        subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Pip command failed: {' '.join(cmd)}")
        raise RuntimeError(f"Dependency installation failed: {e}")


def upgrade_pip(venv_python: Path) -> None:
    """Upgrade pip inside the virtual environment."""
    print("[STATUS] Upgrading pip inside the virtual environment...")
    run_pip_command(venv_python, ["install", "--upgrade", "pip"])


def install_pytorch(venv_python: Path) -> None:
    """Install CPU-only torch and torchvision wheels."""
    print("[STATUS] Installing CPU-only PyTorch and torchvision components...")
    # Get the components from TORCH_CPU_PACKAGES dynamically
    run_pip_command(
        venv_python,
        [
            "install",
            *TORCH_CPU_PACKAGES,
            "--index-url",
            PYTORCH_CPU_INDEX,
        ],
    )


def install_ultralytics(venv_python: Path) -> None:
    """Install Ultralytics package."""
    print("[STATUS] Installing Ultralytics (YOLO)...")
    run_pip_command(venv_python, ["install", "ultralytics"])


def install_core_requirements(venv_python: Path) -> None:
    """Install core requirements from requirements.txt."""
    print(f"[STATUS] Installing core requirements from {REQUIREMENTS_LIGHTWEIGHT.name}...")
    run_pip_command(venv_python, ["install", "-r", str(REQUIREMENTS_LIGHTWEIGHT)])


def install_dev_requirements(venv_python: Path) -> None:
    """Install development requirements from requirements/dev.txt."""
    print(f"[STATUS] Installing development requirements from {REQUIREMENTS_DEV.name}...")
    run_pip_command(venv_python, ["install", "-r", str(REQUIREMENTS_DEV)])


def install_dependencies(
    venv_python: Path,
    missing_install: list[str],
    missing_dev: list[str],
) -> None:
    """Orchestrate installation steps in the strict required order."""
    if not missing_install and not missing_dev:
        return

    try:
        upgrade_pip(venv_python)
    except (RuntimeError, OSError) as e:
        print(f"[ERROR] Failed to upgrade pip: {e}. Attempting to proceed anyway.")

    # Step 2: Install PyTorch CPU if missing
    if any(pkg in missing_install for pkg in TORCH_CPU_PACKAGES):
        install_pytorch(venv_python)

    # Step 3: Install Ultralytics if missing
    if "ultralytics" in missing_install:
        install_ultralytics(venv_python)

    # Step 4: Install remaining core packages from requirements.txt
    if any(pkg in missing_install for pkg in LIGHTWEIGHT_DEPENDENCIES):
        install_core_requirements(venv_python)

    # Step 5: Install dev requirements if requested and missing
    if missing_dev:
        install_dev_requirements(venv_python)
