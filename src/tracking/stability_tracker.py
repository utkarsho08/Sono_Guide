import cv2
import numpy as np

from utils.config import CONFIG


class StabilityTracker:
    """Tracks motion indices using Farneback optical flow and calculates probe stability."""

    def __init__(self, threshold: float | None = None) -> None:
        if threshold is None:
            threshold = CONFIG.tracking.stability_threshold
        self.threshold = threshold
        self.current_stability = 0.0
        self.is_locked = False

        # Optical flow tracking
        self.prev_gray: np.ndarray | None = None

        # Motion score
        self.motion_level = 0.0

        # Lock hysteresis
        self.lock_frames = 0
        self.unlock_frames = 0

    def compute_motion(self, frame: np.ndarray) -> float:
        """Calculate average optical flow magnitude between current and previous frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.prev_gray is None:
            self.prev_gray = gray
            return 0.0

        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray,
            gray,
            None,
            0.5,
            3,
            15,
            3,
            5,
            1.2,
            0
        )

        magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
        motion = float(np.mean(magnitude))

        self.prev_gray = gray
        self.motion_level = motion

        return motion

    def update(self, frame: np.ndarray, confidence: float) -> tuple[float, bool, float]:
        """Update stability metrics and lock status using motion level and confidence."""
        motion = self.compute_motion(frame)

        # Motion threshold for probe stability
        motion_stable = motion < CONFIG.tracking.motion_stable_threshold

        detection_active = confidence > CONFIG.tracking.detection_active_threshold

        # Stability accumulation
        if detection_active and motion_stable:
            self.current_stability = min(
                self.threshold,
                self.current_stability + (1.0 + confidence)
            )
        else:
            self.current_stability = max(
                0.0,
                self.current_stability - CONFIG.tracking.stability_decay
            )

        percentage = (self.current_stability / self.threshold) * 100.0

        # Lock hysteresis to avoid flicker
        if percentage >= 100.0:
            self.lock_frames += 1
            self.unlock_frames = 0
        else:
            self.unlock_frames += 1
            self.lock_frames = 0

        if self.lock_frames > CONFIG.tracking.lock_frames_threshold:
            self.is_locked = True

        if self.unlock_frames > CONFIG.tracking.unlock_frames_threshold:
            self.is_locked = False

        return percentage, self.is_locked, motion

    def reset(self) -> tuple[float, bool, float]:
        """Reset the stability tracker metrics."""
        self.current_stability = 0.0
        self.is_locked = False
        self.lock_frames = 0
        self.unlock_frames = 0
        return 0.0, False, 0.0