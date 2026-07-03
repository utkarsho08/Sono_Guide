import cv2
import threading
import time
from PIL import Image, ImageTk

from utils.utils import Utils
from utils.paths import DEFAULT_VIDEO
from video.calibration_monitor import CalibrationMonitor
from ai.ai_detector import AIDetector
from tracking.stability_tracker import StabilityTracker
from video.auto_freeze import AutoFreeze
from video.overlay_renderer import OverlayRenderer


class VideoEngine:

    def __init__(self, ui, video_path=None):
        if video_path is None:
            video_path = str(DEFAULT_VIDEO)

        self.ui = ui
        self.video_path = video_path
        self.running = False

        # Core components
        self.calibration = CalibrationMonitor()
        self.detector = AIDetector()
        self.stability = StabilityTracker()
        self.freezer = AutoFreeze()
        self.renderer = OverlayRenderer()

        self.cap = None
        self.frame_id = 0

        self.setup_video()

    def setup_video(self):

        try:
            self.cap = cv2.VideoCapture(self.video_path)

            if not self.cap.isOpened():
                print("Video not found. Using simulation mode.")
                self.cap = None

        except Exception as e:
            print("Video setup error:", e)
            self.cap = None

    def start(self):

        self.running = True

        self.thread = threading.Thread(
            target=self.run,
            daemon=True
        )

        self.thread.start()

    def stop(self):

        self.running = False

        if self.cap:
            self.cap.release()

    def get_frame(self):

        if self.cap:

            ret, frame = self.cap.read()

            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                return None

            return frame

        # simulation fallback
        frame = Utils.generate_noise_frame()
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        return frame

    def run(self):

        while self.running:

            frame = self.get_frame()

            if frame is None:
                continue

            frame = Utils.resize_frame(frame)

            # calibration analysis
            brightness, sharpness, alerts = self.calibration.analyze_frame(frame)

            # AI detection
            label, confidence, box = self.detector.detect(frame)

            # stability + motion tracking
            stability_pct, is_locked, motion = self.stability.update(
                frame,
                confidence
            )

            # quality score
            quality = Utils.compute_quality_score(frame)

            # auto capture
            capture_data = None

            if is_locked:

                capture_data = self.freezer.capture_frame(
                    frame,
                    label,
                    confidence,
                    stability_pct
                )

            if capture_data:

                self.ui.root.after(
                    0,
                    self.ui.gallery.add_capture,
                    capture_data
                )

                self.ui.root.after(
                    0,
                    self.ui.flash_screen
                )

                self.stability.reset()

            # render overlays
            display_frame = self.renderer.render(
                frame,
                label,
                confidence,
                box,
                stability_pct,
                alerts
            )

            # update UI
            self.update_ui_frame(display_frame)

            self.ui.root.after(
                0,
                self.ui.update_telemetry,
                brightness,
                sharpness,
                confidence,
                stability_pct
            )

            self.ui.root.after(
                0,
                self.ui.update_alerts,
                alerts
            )

            # status message
            status = label

            if capture_data:
                status = "STANDARD PLANE CAPTURED"

            self.ui.root.after(
                0,
                lambda t=status: self.ui.ai_status_label.config(text=t)
            )

            # update plane label on right panel
            self.ui.root.after(
                0,
                lambda t=label: self.ui.plane_label.config(text=f"STANDARD PLANE: {t.replace('STANDARD PLANE: ', '')}" if "STANDARD PLANE" in t else t)
            )

            # Animate right panel based on stability phase
            if stability_pct >= 80:
                # Stability locked — shrink panel to focus on video
                self.ui.root.after(0, lambda: self.ui.expand_feed(2))
            elif stability_pct >= 30:
                # Acquiring — partially shrink panel
                self.ui.root.after(0, lambda: self.ui.expand_feed(1))
            else:
                # Low confidence — full panel visible
                self.ui.root.after(0, lambda: self.ui.expand_feed(0))

            time.sleep(1/30)

    def update_ui_frame(self, frame):

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        img = Image.fromarray(frame_rgb)

        win_w = self.ui.feed_label.winfo_width()
        win_h = self.ui.feed_label.winfo_height()

        if win_w > 1 and win_h > 1:

            img = img.resize(
                (win_w, win_h),
                Image.Resampling.LANCZOS
            )

        img_tk = ImageTk.PhotoImage(image=img)

        self.ui.feed_label.after(
            0,
            self.update_feed_label,
            img_tk
        )

    def update_feed_label(self, img_tk):

        self.ui.feed_label.configure(image=img_tk)
        self.ui.feed_label.image = img_tk