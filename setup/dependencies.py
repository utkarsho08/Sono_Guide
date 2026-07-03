"""
Dependency metadata for Sono-Guide cross-platform bootstrap.

This module acts as the single source of truth for the launcher.
It dynamically parses dependency manifests (requirements.txt, etc.)
so that dependency changes only need to be configured in the requirements files.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Central filesystem locations
PROJECT_ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = PROJECT_ROOT / ".venv"

REQUIREMENTS_LIGHTWEIGHT = PROJECT_ROOT / "requirements.txt"
REQUIREMENTS_AI = PROJECT_ROOT / "requirements" / "ai.txt"
REQUIREMENTS_OPTIONAL = PROJECT_ROOT / "requirements" / "optional.txt"
REQUIREMENTS_DEV = PROJECT_ROOT / "requirements" / "dev.txt"


def _parse_manifest(filepath: Path) -> list[str]:
    """Parse clean package names from a requirements file."""
    packages = []
    if not filepath.is_file():
        return packages
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Ignore empty lines, comments, and pip flags
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            # Extract name before inline comments or version specifiers
            parts = line.split("#")[0].strip()
            for op in ("==", ">=", "<=", ">", "<", "~=", ";"):
                parts = parts.split(op)[0].strip()
            if parts:
                packages.append(parts)
    return packages


def _get_pytorch_index_url(filepath: Path) -> str:
    """Extract PyTorch CPU index URL from the heavy AI manifest."""
    default_url = "https://download.pytorch.org/whl/cpu"
    if not filepath.is_file():
        return default_url
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("--extra-index-url") or line.startswith("--index-url"):
                parts = line.split()
                if len(parts) > 1:
                    return parts[1]
    return default_url


# Dynamically loaded dependency tuples
LIGHTWEIGHT_DEPENDENCIES = tuple(_parse_manifest(REQUIREMENTS_LIGHTWEIGHT))
HEAVY_AI_DEPENDENCIES = tuple(_parse_manifest(REQUIREMENTS_AI))
OPTIONAL_DEPENDENCIES = tuple(_parse_manifest(REQUIREMENTS_OPTIONAL))
DEVELOPMENT_DEPENDENCIES = tuple(_parse_manifest(REQUIREMENTS_DEV))

# Dynamically loaded CPU index URL
PYTORCH_CPU_INDEX = _get_pytorch_index_url(REQUIREMENTS_AI)

# Filter torch CPU packages dynamically from heavy AI dependencies
TORCH_CPU_PACKAGES = tuple(
    pkg for pkg in HEAVY_AI_DEPENDENCIES if pkg in ("torch", "torchvision", "torchaudio")
)

AI_REQUIREMENTS_FILE = REQUIREMENTS_AI

# Mapping for package verification fallbacks
PACKAGE_IMPORT_NAMES = {
    "torch": "torch",
    "torchvision": "torchvision",
    "ultralytics": "ultralytics",
    "numpy": "numpy",
    "opencv-python": "cv2",
    "pillow": "PIL",
}


@dataclass(frozen=True)
class InstallStage:
    name: str
    description: str


# Setup orchestration stages info
INSTALL_STAGES = (
    InstallStage("upgrade-pip", "Upgrade pip inside the project virtual environment"),
    InstallStage(
        "pytorch-cpu",
        "Install CPU-only torch and torchvision from PyTorch wheel index",
    ),
    InstallStage("ultralytics", "Install Ultralytics YOLO stack"),
    InstallStage(
        "lightweight",
        "Install numpy, opencv-python, pillow from requirements.txt",
    ),
    InstallStage("launch", "Run main.py with the virtual environment interpreter"),
)
