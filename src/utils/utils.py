from datetime import datetime
from pathlib import Path
import cv2
import numpy as np

from utils.config import CONFIG


class Utils:
    """General utility methods for file operations, frame processing, and image quality metrics."""

    @staticmethod
    def create_dir(directory: Path | str) -> None:
        """Create directory recursively if it does not already exist."""
        Path(directory).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_timestamp() -> str:
        """Generate a microsecond-accurate timestamp string."""
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    @staticmethod
    def resize_frame(frame: np.ndarray, max_width: int = None) -> np.ndarray:
        """Resize frame preserving aspect ratio if its width exceeds max_width."""
        if max_width is None:
            max_width = CONFIG.video.max_width

        h, w = frame.shape[:2]

        if w <= max_width:
            return frame

        ratio = max_width / w
        new_size = (int(w * ratio), int(h * ratio))

        return cv2.resize(frame, new_size, interpolation=cv2.INTER_AREA)

    @staticmethod
    def normalize_frame(frame: np.ndarray) -> np.ndarray:
        """Normalize pixel intensities to the full uint8 [0-255] range."""
        frame = frame.astype(np.float32)
        frame = (frame - frame.min()) / (frame.max() - frame.min() + 1e-6)
        frame = (frame * 255).astype(np.uint8)

        return frame

    # ---------------------------
    # Ultrasound Preprocessing
    # ---------------------------
    @staticmethod
    def preprocess_ultrasound(frame: np.ndarray) -> np.ndarray:
        """Apply adaptive histogram equalization and speckle filtering to raw frames."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # speckle reduction
        gray = cv2.medianBlur(gray, 5)

        # adaptive contrast enhancement
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        gray = clahe.apply(gray)

        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    # ---------------------------
    # Image Quality Metrics
    # ---------------------------
    @staticmethod
    def compute_brightness(frame: np.ndarray) -> float:
        """Calculate mean intensity across the grayscale channel."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return float(np.mean(gray))

    @staticmethod
    def compute_sharpness(frame: np.ndarray) -> float:
        """Evaluate focus level using Laplacian variance."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())

    @staticmethod
    def compute_contrast(frame: np.ndarray) -> float:
        """Evaluate contrast deviation using grayscale standard deviation."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return float(gray.std())

    @staticmethod
    def compute_quality_score(frame: np.ndarray) -> float:
        """Assess overall image quality based on brightness, sharpness, and contrast."""
        brightness = Utils.compute_brightness(frame)
        sharpness = Utils.compute_sharpness(frame)
        contrast = Utils.compute_contrast(frame)

        brightness_score = min(brightness / CONFIG.output.quality_brightness_norm, 1.0)
        sharpness_score = min(sharpness / CONFIG.output.quality_sharpness_norm, 1.0)
        contrast_score = min(contrast / CONFIG.output.quality_contrast_norm, 1.0)

        quality = (
            brightness_score * 0.3 +
            sharpness_score * 0.4 +
            contrast_score * 0.3
        )

        return quality * 100.0

    # ---------------------------
    # Demo Frame Generator
    # ---------------------------
    @staticmethod
    def generate_noise_frame(width: int = 640, height: int = 480) -> np.ndarray:
        """Synthesize artificial ultrasound noise frame with mock anatomical shapes."""
        # base speckle noise
        noise = np.random.normal(120, 25, (height, width)).astype(np.uint8)

        # blur to mimic ultrasound speckle
        noise = cv2.GaussianBlur(noise, (5, 5), 0)

        # add circular structures (simulate anatomy)
        for _ in range(np.random.randint(1, 4)):

            cx = np.random.randint(100, width - 100)
            cy = np.random.randint(100, height - 100)
            radius = np.random.randint(40, 90)

            cv2.circle(
                noise,
                (cx, cy),
                radius,
                np.random.randint(160, 200),
                2
            )

        return noise