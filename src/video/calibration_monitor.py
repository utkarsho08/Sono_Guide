from utils.config import CONFIG
import cv2
import numpy as np


class CalibrationMonitor:
    def __init__(self):

        # Thresholds tuned for ultrasound-like images
        self.brightness_low = CONFIG.video.brightness_low
        self.brightness_high = CONFIG.video.brightness_high

        self.sharpness_threshold = CONFIG.video.sharpness_threshold
        self.contrast_threshold = CONFIG.video.contrast_threshold
        self.noise_threshold = CONFIG.video.noise_threshold

    def compute_brightness(self, gray):
        return np.mean(gray)

    def compute_sharpness(self, gray):
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    def compute_contrast(self, gray):
        return gray.std()

    def compute_noise(self, gray):
        blur = cv2.GaussianBlur(gray, CONFIG.video.gaussian_blur_kernel, 0)
        noise = np.mean(np.abs(gray - blur))
        return noise

    def analyze_frame(self, frame):

        if frame is None:
            return 0, 0, []

        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame

        brightness = self.compute_brightness(gray)
        sharpness = self.compute_sharpness(gray)
        contrast = self.compute_contrast(gray)
        noise = self.compute_noise(gray)

        alerts = []

        # Gain checks
        if brightness < self.brightness_low:
            alerts.append("LOW GAIN – INCREASE ULTRASOUND GAIN")

        if brightness > self.brightness_high:
            alerts.append("GAIN TOO HIGH – REDUCE GAIN")

        # Probe focus
        if sharpness < self.sharpness_threshold:
            alerts.append("IMAGE BLURRY – ADJUST PROBE ANGLE")

        # Dynamic range
        if contrast < self.contrast_threshold:
            alerts.append("LOW CONTRAST – ADJUST DEPTH OR TGC")

        # Speckle noise
        if noise > self.noise_threshold:
            alerts.append("HIGH SPECKLE – REDUCE GAIN")

        return brightness, sharpness, alerts