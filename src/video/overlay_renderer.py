
import cv2
import numpy as np


class OverlayRenderer:
    def __init__(self):
        self.primary_color = (0, 229, 255)    # Cyan (locked)
        self.secondary_color = (0, 165, 255)  # Orange (acquiring)
        self.alert_color = (0, 0, 255)        # Red (alerts)
        self.text_color = (255, 255, 255)
        self.grid_color = (90, 90, 90)
        self.guidance_color = (0, 255, 255)   # Yellow
        self.locked_color = (0, 255, 0)       # Green (stability locked)
        self.low_conf_color = (0, 0, 255)     # Red (low confidence)

        self.scanline_y = 0

    # ---------- utility ----------
    def normalize_box(self, box, frame_shape=None):
        if box is None:
            return None

        try:
            b = np.array(box).flatten()
            if len(b) < 4:
                return None
            x1, y1, x2, y2 = int(b[0]), int(b[1]), int(b[2]), int(b[3])
            if frame_shape is not None:
                h, w = frame_shape[:2]
                x1 = max(0, min(x1, w - 1))
                x2 = max(0, min(x2, w - 1))
                y1 = max(0, min(y1, h - 1))
                y2 = max(0, min(y2, h - 1))
            # Ensure box has minimum size
            if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
                return None
            return [x1, y1, x2, y2]
        except:
            return None

    # ---------- grid ----------
    def draw_grid(self, frame):
        h, w = frame.shape[:2]
        grid = frame.copy()

        for i in range(1, 3):
            cv2.line(grid, (int(w*i/3), 0), (int(w*i/3), h), self.grid_color, 1)
            cv2.line(grid, (0, int(h*i/3)), (w, int(h*i/3)), self.grid_color, 1)

        return cv2.addWeighted(grid, 0.18, frame, 0.82, 0)

    # ---------- scanline ----------
    def draw_scanline(self, frame):
        h, w = frame.shape[:2]
        self.scanline_y = (self.scanline_y + 4) % h
        cv2.line(frame, (0, self.scanline_y), (w, self.scanline_y), (40, 40, 40), 1)

    # ---------- crosshair ----------
    def draw_crosshair(self, frame):
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        cv2.drawMarker(frame, (cx, cy), (140,140,140), cv2.MARKER_CROSS, 22, 1)

    # ---------- bounding box ----------
    def draw_box(self, frame, box, label, stability_pct, confidence):

        box = self.normalize_box(box, frame.shape)
        if box is None:
            return

        x1, y1, x2, y2 = box

        # Color based on stability: red → orange → green
        if stability_pct >= 80:
            state_color = self.locked_color       # Green: locked
        elif stability_pct >= 40:
            state_color = self.secondary_color    # Orange: acquiring
        else:
            state_color = self.low_conf_color     # Red: low confidence

        # Corner lengths proportional to box size
        bw = x2 - x1
        bh = y2 - y1
        length = max(15, min(30, int(min(bw, bh) * 0.15)))
        thickness = 2

        # Top-left
        cv2.line(frame, (x1, y1), (x1 + length, y1), state_color, thickness)
        cv2.line(frame, (x1, y1), (x1, y1 + length), state_color, thickness)
        # Top-right
        cv2.line(frame, (x2, y1), (x2 - length, y1), state_color, thickness)
        cv2.line(frame, (x2, y1), (x2, y1 + length), state_color, thickness)
        # Bottom-left
        cv2.line(frame, (x1, y2), (x1 + length, y2), state_color, thickness)
        cv2.line(frame, (x1, y2), (x1, y2 - length), state_color, thickness)
        # Bottom-right
        cv2.line(frame, (x2, y2), (x2 - length, y2), state_color, thickness)
        cv2.line(frame, (x2, y2), (x2, y2 - length), state_color, thickness)

        label_text = f"{label}  {int(confidence * 100)}%"
        cv2.putText(frame, label_text, (x1, max(y1 - 10, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, state_color, 1)

    # ---------- guidance ----------
    def draw_guidance(self, frame, box):

        box = self.normalize_box(box, frame.shape)
        if box is None:
            return

        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2

        x1, y1, x2, y2 = box
        bx, by = (x1 + x2) // 2, (y1 + y2) // 2

        guidance = ""

        if bx < cx - 40:
            guidance += "MOVE RIGHT"
        elif bx > cx + 40:
            guidance += "MOVE LEFT"

        if by < cy - 40:
            guidance += (" " if guidance else "") + "MOVE DOWN"
        elif by > cy + 40:
            guidance += (" " if guidance else "") + "MOVE UP"

        if guidance:
            text_size = cv2.getTextSize(guidance, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            text_x = cx - text_size[0] // 2
            text_y = cy + 80
            # Shadow for readability
            cv2.putText(frame, guidance, (text_x + 2, text_y + 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)
            cv2.putText(frame, guidance, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.guidance_color, 2)

    # ---------- stability ----------
    def draw_stability_bar(self, frame, stability_pct):

        h, w = frame.shape[:2]

        bar_w = 240
        bar_h = 16

        bar_x = w - bar_w - 30
        bar_y = h - 60

        cv2.rectangle(frame,
                      (bar_x, bar_y),
                      (bar_x + bar_w, bar_y + bar_h),
                      (30, 30, 30),
                      -1)

        fill_w = int(bar_w * (stability_pct / 100))

        if stability_pct >= 80:
            color = self.locked_color        # Green
        elif stability_pct >= 40:
            color = self.secondary_color     # Orange
        else:
            color = self.low_conf_color      # Red

        cv2.rectangle(frame,
                      (bar_x, bar_y),
                      (bar_x + fill_w, bar_y + bar_h),
                      color,
                      -1)

        label = "STABILITY LOCK" if stability_pct >= 80 else "ACQUIRING"

        cv2.putText(frame,
                    f"{label}  {int(stability_pct)}%",
                    (bar_x, bar_y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    self.text_color,
                    1)

    # ---------- heatmap ----------
    def draw_heatmap(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        heat = cv2.applyColorMap(
            cv2.normalize(gray,None,0,255,cv2.NORM_MINMAX),
            cv2.COLORMAP_JET
        )

        return cv2.addWeighted(frame,0.7,heat,0.3,0)

    # ---------- watermark ----------
    def draw_watermark(self, frame):

        h, w = frame.shape[:2]

        cv2.putText(
            frame,
            "GENDER DETECTION DISABLED - PC-PNDT COMPLIANT",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (200, 200, 255),
            1
        )

    # ---------- render ----------
    def render(self, frame, label, confidence, box, stability_pct, alerts):

        if frame is None:
            return None

        output = frame.copy()

        output = self.draw_grid(output)

        output = self.draw_heatmap(output)

        self.draw_scanline(output)

        self.draw_crosshair(output)

        self.draw_guidance(output, box)

        self.draw_box(output, box, label, stability_pct, confidence)

        self.draw_stability_bar(output, stability_pct)

        self.draw_watermark(output)

        # Prominent red alert text at top of frame (matches demo)
        if alerts:
            alert_text = "  ???  ".join(alerts)
            # Shadow
            cv2.putText(output, alert_text, (22, 42),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 4)
            # Foreground red
            cv2.putText(output, alert_text, (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)

        return output
