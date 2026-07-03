"""
AI inference package.

Heavy dependencies (torch, torchvision, ultralytics) are installed separately
via launcher.py. See src/ai/deps.py and docs/DEPENDENCY_PLAN.md.
"""

from .ai_detector import AIDetector
from .deps import HEAVY_DEPENDENCIES

__all__ = ["AIDetector", "HEAVY_DEPENDENCIES"]
