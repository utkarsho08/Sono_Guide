from pathlib import Path
import cv2
import time
import numpy as np
from utils.utils import Utils
from utils.paths import OUTPUT_DIR
from utils.config import CONFIG


class AutoFreeze:
    def __init__(self, output_dir=None):
        if output_dir is None:
            output_dir = OUTPUT_DIR
        self.output_dir = Path(output_dir)
        Utils.create_dir(self.output_dir)

        # Best frame buffer
        self.best_frame = None
        self.best_score = 0

        # Frame collection window
        self.window_start = None
        self.window_duration = CONFIG.output.window_duration  # seconds

        # Prevent repeated captures
        self.cooldown_time = CONFIG.output.cooldown_time
        self.last_capture_time = 0

    def compute_frame_quality(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        brightness = np.mean(gray)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

        brightness_score = min(brightness / CONFIG.output.quality_brightness_norm, 1.0)
        sharpness_score = min(sharpness / CONFIG.output.quality_sharpness_norm, 1.0)

        quality = (
            CONFIG.output.quality_brightness_weight * brightness_score +
            CONFIG.output.quality_sharpness_weight * sharpness_score
        )

        return quality * 100

    def compute_score(self, confidence, stability, quality):
        return (
            confidence * CONFIG.output.score_confidence_weight +
            (stability / 100) * CONFIG.output.score_stability_weight +
            (quality / 100) * CONFIG.output.score_quality_weight
        )

    def capture_frame(self, frame, label, confidence, stability):

        if frame is None:
            return None

        current_time = time.time()

        # cooldown protection
        if current_time - self.last_capture_time < self.cooldown_time:
            return None

        quality = self.compute_frame_quality(frame)

        score = self.compute_score(confidence, stability, quality)

        # start window
        if self.window_start is None:
            self.window_start = current_time
            self.best_frame = frame.copy()
            self.best_score = score

        # update best frame
        if score > self.best_score:
            self.best_frame = frame.copy()
            self.best_score = score

        # window complete
        if current_time - self.window_start >= self.window_duration:

            timestamp = Utils.get_timestamp()
            filename = f"capture_{timestamp}.jpg"
            filepath = self.output_dir / filename

            cv2.imwrite(str(filepath), self.best_frame)

            capture_data = {
                'path': str(filepath),
                'timestamp': timestamp,
                'label': label,
                'confidence': confidence,
                'stability': stability,
                'quality': quality,
                'score': self.best_score
            }

            # reset window
            self.window_start = None
            self.best_frame = None
            self.best_score = 0
            self.last_capture_time = current_time

            return capture_data

        return None