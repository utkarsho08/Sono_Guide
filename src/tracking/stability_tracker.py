from utils.config import CONFIG
import cv2
import numpy as np


class StabilityTracker:
    def __init__(self, threshold=None):
        if threshold is None:
            threshold = CONFIG.tracking.stability_threshold
        self.threshold = threshold
        self.current_stability = 0
        self.is_locked = False

        # Optical flow tracking
        self.prev_gray = None

        # Motion score
        self.motion_level = 0

        # Lock hysteresis
        self.lock_frames = 0
        self.unlock_frames = 0

    def compute_motion(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.prev_gray is None:
            self.prev_gray = gray
            return 0

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
        motion = np.mean(magnitude)

        self.prev_gray = gray
        self.motion_level = motion

        return motion

    def update(self, frame, confidence):
        motion = self.compute_motion(frame)

        # Motion threshold for probe stability
        motion_stable = motion < CONFIG.tracking.motion_stable_threshold

        detection_active = confidence > CONFIG.tracking.detection_active_threshold

        # Stability accumulation
        if detection_active and motion_stable:
            self.current_stability = min(
                self.threshold,
                self.current_stability + (1 + confidence)
            )
        else:
            self.current_stability = max(
                0,
                self.current_stability - CONFIG.tracking.stability_decay
            )

        percentage = (self.current_stability / self.threshold) * 100

        # Lock hysteresis to avoid flicker
        if percentage >= 100:
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

    def reset(self):
        self.current_stability = 0
        self.is_locked = False
        self.lock_frames = 0
        self.unlock_frames = 0
        return 0.0, False, 0.0