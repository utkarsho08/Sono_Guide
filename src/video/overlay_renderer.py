import cv2
import numpy as np

from utils.config import CONFIG


class OverlayRenderer:
    """Renders visual indicators, grid lines, heatmaps, standard plane boxes, and telemetry HUD overlays."""

    def __init__(self) -> None:
        self.primary_color = CONFIG.overlay.primary_color
        self.secondary_color = CONFIG.overlay.secondary_color
        self.alert_color = CONFIG.overlay.alert_color
        self.text_color = CONFIG.overlay.text_color
        self.grid_color = CONFIG.overlay.grid_color
        self.guidance_color = CONFIG.overlay.guidance_color
        self.locked_color = CONFIG.overlay.locked_color
        self.low_conf_color = CONFIG.overlay.low_conf_color

        self.scanline_y = 0

    # ---------- utility ----------
    def normalize_box(self, box: list[float] | None, frame_shape: tuple[int, ...] | None = None) -> list[int] | None:
        """Sanitize and clamp floating point boxes into integer pixel coordinates."""
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
        except (ValueError, TypeError, IndexError):
            return None

    # ---------- grid ----------
    def draw_grid(self, frame: np.ndarray) -> np.ndarray:
        """Draw a symmetric 3x3 reference grid with configured transparency."""
        h, w = frame.shape[:2]
        grid = frame.copy()

        for i in range(1, 3):
            cv2.line(grid, (int(w*i/3), 0), (int(w*i/3), h), self.grid_color, 1)
            cv2.line(grid, (0, int(h*i/3)), (w, int(h*i/3)), self.grid_color, 1)

        return cv2.addWeighted(grid, CONFIG.overlay.grid_alpha, frame, CONFIG.overlay.grid_beta, 0)

    # ---------- scanline ----------
    def draw_scanline(self, frame: np.ndarray) -> None:
        """Draw an animated diagnostic scanline sweeping vertically across the feed."""
        h, w = frame.shape[:2]
        self.scanline_y = (self.scanline_y + CONFIG.overlay.scanline_step) % h
        cv2.line(frame, (0, self.scanline_y), (w, self.scanline_y), CONFIG.overlay.scanline_color, 1)

    # ---------- crosshair ----------
    def draw_crosshair(self, frame: np.ndarray) -> None:
        """Draw a static center crosshair marker to assist with probe alignment."""
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        cv2.drawMarker(frame, (cx, cy), CONFIG.overlay.crosshair_color, cv2.MARKER_CROSS, CONFIG.overlay.crosshair_marker_size, CONFIG.overlay.crosshair_thickness)

    # ---------- bounding box ----------
    def draw_box(self, frame: np.ndarray, box: list[float] | None, label: str, stability_pct: float, confidence: float) -> None:
        """Draw standard plane corner bounding box overlays."""
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
        length = max(
            CONFIG.overlay.corner_min_len,
            min(CONFIG.overlay.corner_max_len, int(min(bw, bh) * CONFIG.overlay.corner_ratio))
        )
        thickness = CONFIG.overlay.corner_thickness

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
    def draw_guidance(self, frame: np.ndarray, box: list[float] | None) -> None:
        """Draw directional arrow cues guiding the operator toward the center screen."""
        box = self.normalize_box(box, frame.shape)
        if box is None:
            return

        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2

        x1, y1, x2, y2 = box
        bx, by = (x1 + x2) // 2, (y1 + y2) // 2

        guidance = ""

        if bx < cx - CONFIG.overlay.guidance_margin:
            guidance += "MOVE RIGHT"
        elif bx > cx + CONFIG.overlay.guidance_margin:
            guidance += "MOVE LEFT"

        if by < cy - CONFIG.overlay.guidance_margin:
            guidance += (" " if guidance else "") + "MOVE DOWN"
        elif by > cy + CONFIG.overlay.guidance_margin:
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
    def draw_stability_bar(self, frame: np.ndarray, stability_pct: float) -> None:
        """Draw stability accumulation HUD bar overlay."""
        h, w = frame.shape[:2]

        bar_w = CONFIG.overlay.stability_bar_width
        bar_h = CONFIG.overlay.stability_bar_height

        bar_x = w - bar_w - CONFIG.overlay.stability_bar_margin_x
        bar_y = h - CONFIG.overlay.stability_bar_margin_y

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
    def draw_heatmap(self, frame: np.ndarray) -> np.ndarray:
        """Apply a jet colormap to highlight high-contrast anatomical features."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        heat = cv2.applyColorMap(
            cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX),
            cv2.COLORMAP_JET
        )

        return cv2.addWeighted(frame, CONFIG.overlay.heatmap_alpha, heat, CONFIG.overlay.heatmap_beta, 0)

    # ---------- watermark ----------
    def draw_watermark(self, frame: np.ndarray) -> None:
        """Render PC-PNDT compliance warnings at the bottom of the feed."""
        h, w = frame.shape[:2]

        cv2.putText(
            frame,
            CONFIG.overlay.watermark_text,
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            CONFIG.overlay.watermark_color,
            1
        )

    # ---------- render ----------
    def render(self, frame: np.ndarray | None, label: str, confidence: float, box: list[float] | None, stability_pct: float, alerts: list[str]) -> np.ndarray | None:
        """Render the complete sequence of HUD diagnostics over the raw image frame."""
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
            alert_text = CONFIG.overlay.alert_separator.join(alerts)
            # Shadow
            cv2.putText(output, alert_text, (22, 42),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 4)
            # Foreground red
            cv2.putText(output, alert_text, (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)

        return output
