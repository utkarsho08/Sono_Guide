import cv2
import numpy as np
from datetime import datetime
from pathlib import Path


class Utils:

    # ---------------------------
    # File Utilities
    # ---------------------------
    @staticmethod
    def create_dir(directory):
        Path(directory).mkdir(parents=True, exist_ok=True)


    @staticmethod
    def get_timestamp():
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    # ---------------------------
    # Frame Utilities
    # ---------------------------
    @staticmethod
    def resize_frame(frame, max_width=960):

        h, w = frame.shape[:2]

        if w <= max_width:
            return frame

        ratio = max_width / w
        new_size = (int(w * ratio), int(h * ratio))

        return cv2.resize(frame, new_size, interpolation=cv2.INTER_AREA)

    @staticmethod
    def normalize_frame(frame):

        frame = frame.astype(np.float32)
        frame = (frame - frame.min()) / (frame.max() - frame.min() + 1e-6)
        frame = (frame * 255).astype(np.uint8)

        return frame

    # ---------------------------
    # Ultrasound Preprocessing
    # ---------------------------
    @staticmethod
    def preprocess_ultrasound(frame):

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
    def compute_brightness(frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return float(np.mean(gray))

    @staticmethod
    def compute_sharpness(frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())

    @staticmethod
    def compute_contrast(frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return float(gray.std())

    @staticmethod
    def compute_quality_score(frame):

        brightness = Utils.compute_brightness(frame)
        sharpness = Utils.compute_sharpness(frame)
        contrast = Utils.compute_contrast(frame)

        brightness_score = min(brightness / 150, 1.0)
        sharpness_score = min(sharpness / 200, 1.0)
        contrast_score = min(contrast / 60, 1.0)

        quality = (
            brightness_score * 0.3 +
            sharpness_score * 0.4 +
            contrast_score * 0.3
        )

        return quality * 100

    # ---------------------------
    # Demo Frame Generator
    # ---------------------------
    @staticmethod
    def generate_noise_frame(width=640, height=480):

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