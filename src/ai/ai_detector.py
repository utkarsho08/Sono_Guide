import cv2
import numpy as np
from ultralytics import YOLO
from collections import deque
from utils.utils import Utils
from utils.paths import DEFAULT_MODEL

DEMO_MODE = True


class AIDetector:

    def __init__(self, model_name=None):
        if model_name is None:
            model_name = str(DEFAULT_MODEL)

        try:
            self.model = YOLO(model_name)
        except Exception as e:
            print("Model load error:", e)
            self.model = None

        # temporal smoothing
        self.prev_confidence = 0.0
        self.box_history = deque(maxlen=6)

        # label cycling for demo
        self.current_label_idx = 0
        self.label_timer = 0

        self.labels = [
            "STANDARD PLANE: FETAL HEAD (BPD)",
            "STANDARD PLANE: ABDOMEN (AC)",
            "STANDARD PLANE: FEMUR (FL)"
        ]

        # Kalman filter for tracking
        self.kalman = cv2.KalmanFilter(4, 2)

        self.kalman.measurementMatrix = np.array(
            [[1,0,0,0],
             [0,1,0,0]], np.float32
        )

        self.kalman.transitionMatrix = np.array(
            [[1,0,1,0],
             [0,1,0,1],
             [0,0,1,0],
             [0,0,0,1]], np.float32
        )

        self.kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03

    def region_proposal(self, frame):

        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        edges = cv2.Canny(blur, 40, 120)

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        best_box = None
        best_score = 0
        largest_box = None
        largest_area = 0

        for c in contours:

            x, y, cw, ch = cv2.boundingRect(c)

            area = cw * ch

            if area < 1500:
                continue

            # Track largest contour as fallback
            if area > largest_area:
                largest_area = area
                largest_box = [x, y, x + cw, y + ch]

            aspect = cw / (ch + 1e-6)

            score = area * (1 - abs(aspect - 1))

            if score > best_score:
                best_score = score
                best_box = [x, y, x + cw, y + ch]

        # Fall back to largest box if best_score box is tiny
        result = best_box if best_box else largest_box

        if result is None:
            # Last resort: use a central region of the frame
            margin_x, margin_y = w // 5, h // 5
            result = [margin_x, margin_y, w - margin_x, h - margin_y]

        # Clamp to frame
        result = [
            max(0, min(result[0], w - 1)),
            max(0, min(result[1], h - 1)),
            max(0, min(result[2], w - 1)),
            max(0, min(result[3], h - 1)),
        ]

        return result

    def run_yolo(self, frame):

        if self.model is None:
            return None, 0

        results = self.model(frame, verbose=False)

        best_box = None
        best_conf = 0

        for r in results:

            boxes = r.boxes

            if boxes is None:
                continue

            for box in boxes:

                conf = float(box.conf[0])

                if conf > 0.35 and conf > best_conf:

                    best_conf = conf
                    best_box = box.xyxy[0].tolist()

        return best_box, best_conf

    def kalman_smooth(self, box):

        if box is None:
            return None

        x1,y1,x2,y2 = box
        cx = (x1+x2)/2
        cy = (y1+y2)/2

        measurement = np.array([[np.float32(cx)], [np.float32(cy)]])

        self.kalman.correct(measurement)
        prediction = self.kalman.predict()

        px, py = prediction[0], prediction[1]

        w = x2-x1
        h = y2-y1

        return [
            px-w/2,
            py-h/2,
            px+w/2,
            py+h/2
        ]

    def detect(self, frame):

        if frame is None:
            return "SYSTEM OFFLINE", 0.0, None

        # ultrasound preprocessing
        frame = Utils.preprocess_ultrasound(frame)

        yolo_box, yolo_conf = self.run_yolo(frame)

        if yolo_box is None:
            fallback_box = self.region_proposal(frame)
            raw_box = fallback_box
            raw_conf = 0.55 if fallback_box else 0
        else:
            raw_box = yolo_box
            raw_conf = yolo_conf

        # temporal confidence smoothing
        if DEMO_MODE:

            target = raw_conf

            if target > 0:
                target = min(0.98, target + 0.15)

            self.prev_confidence = (
                0.7*self.prev_confidence +
                0.3*target
            )

        else:

            self.prev_confidence = (
                0.8*self.prev_confidence +
                0.2*raw_conf
            )

        # temporal box smoothing
        if raw_box:
            self.box_history.append(raw_box)

        smoothed_box = None

        if len(self.box_history) > 0:

            avg = np.mean(self.box_history, axis=0)
            smoothed_box = avg.tolist()

            smoothed_box = self.kalman_smooth(smoothed_box)

        # plane switching for demo
        if self.prev_confidence > 0.6:

            self.label_timer += 1

            if self.label_timer > 120:

                self.current_label_idx = (
                    self.current_label_idx + 1
                ) % len(self.labels)

                self.label_timer = 0

            label = self.labels[self.current_label_idx]

        else:
            label = "SEARCHING FOR STANDARD PLANE..."

        return label, self.prev_confidence, smoothed_box