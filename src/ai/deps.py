"""
Heavy AI dependency boundary for src.ai.

These packages are required for YOLO inference but are installed separately
by launcher.py using CPU-only PyTorch wheels. They must not appear in the
root requirements.txt file.
"""

from setup.dependencies import (
    HEAVY_AI_DEPENDENCIES,
    PYTORCH_CPU_INDEX,
)

HEAVY_DEPENDENCIES = HEAVY_AI_DEPENDENCIES
AI_REQUIREMENTS_FILE = "requirements/ai.txt"

