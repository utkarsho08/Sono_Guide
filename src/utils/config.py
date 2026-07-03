"""
Centralized, immutable configuration system for Sono-Guide.

This module houses all system variables organized into frozen, logical dataclasses.
It uses pathlib.Path throughout and avoids mutable global state.
"""

from dataclasses import dataclass
from pathlib import Path

# Resolve project root dynamically (two levels up from src/utils/config.py)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ProjectConfig:
    """Project-wide filesystem paths and metadata configurations."""
    root: Path = PROJECT_ROOT
    assets_dir: Path = PROJECT_ROOT / "assets"
    models_dir: Path = assets_dir / "models"
    images_dir: Path = assets_dir / "images"
    output_dir: Path = PROJECT_ROOT / "output"
    logs_dir: Path = PROJECT_ROOT / "logs"

    requirements_txt: Path = PROJECT_ROOT / "requirements.txt"
    requirements_ai: Path = PROJECT_ROOT / "requirements" / "ai.txt"
    requirements_dev: Path = PROJECT_ROOT / "requirements" / "dev.txt"
    requirements_optional: Path = PROJECT_ROOT / "requirements" / "optional.txt"

    venv_dir: Path = PROJECT_ROOT / ".venv"
    default_model: Path = models_dir / "best.pt"
    default_video: Path = images_dir / "ultrasound_demo.mp4"


@dataclass(frozen=True)
class ModelConfig:
    """Model properties and default file path bindings."""
    default_model: Path = ProjectConfig.default_model
    default_video: Path = ProjectConfig.default_video


@dataclass(frozen=True)
class DetectionConfig:
    """AI detection algorithms, Kalman tracking, and demo sequence parameters."""
    confidence_threshold: float = 0.35
    history_len: int = 6
    kalman_process_noise: float = 0.03
    region_area_threshold: int = 1500
    region_gaussian_blur: tuple[int, int] = (5, 5)
    region_canny_low: int = 40
    region_canny_high: int = 120
    demo_mode_confidence_limit: float = 0.98
    demo_mode_confidence_boost: float = 0.15
    demo_mode_smoothing_factor: float = 0.7
    normal_mode_smoothing_factor: float = 0.8
    plane_switch_frames: int = 120
    labels: tuple[str, ...] = (
        "STANDARD PLANE: FETAL HEAD (BPD)",
        "STANDARD PLANE: ABDOMEN (AC)",
        "STANDARD PLANE: FEMUR (FL)"
    )


@dataclass(frozen=True)
class TrackingConfig:
    """Stability indices, motion scoring, and status locks properties."""
    stability_threshold: float = 40.0
    motion_stable_threshold: float = 0.8
    detection_active_threshold: float = 0.5
    stability_decay: float = 3.0
    lock_frames_threshold: int = 3
    unlock_frames_threshold: int = 5


@dataclass(frozen=True)
class VideoConfig:
    """Ingestion timing, frame limits, and hardware calibration parameters."""
    frame_delay: float = 1.0 / 30.0
    max_width: int = 960

    # Calibration thresholds
    brightness_low: float = 40.0
    brightness_high: float = 200.0
    sharpness_threshold: float = 90.0
    contrast_threshold: float = 35.0
    noise_threshold: float = 55.0
    gaussian_blur_kernel: tuple[int, int] = (5, 5)


@dataclass(frozen=True)
class UIConfig:
    """User Interface fonts, dimensions, layouts, and colors configurations."""
    title: str = "Sono-Guide – Professional AI Ultrasound Station"
    geometry: str = "1400x900"
    min_width: int = 900
    min_height: int = 600

    bg_main: str = "#0A0F14"
    bg_panel: str = "#111821"
    bg_statbar_bg: str = "#1a242f"
    bg_canvas: str = "#1a1a1a"
    bg_thumbnail_container: str = "#2d2d2d"

    fg_logo: str = "#00E5FF"
    fg_white: str = "#ffffff"
    fg_orange: str = "#FFA500"
    fg_red: str = "#ff3333"

    font_logo: tuple[str, int, str] = ("Arial", 18, "bold")
    font_patient: tuple[str, int] = ("Arial", 10)
    font_section: tuple[str, int, str] = ("Arial", 11, "bold")
    font_telemetry: tuple[str, int, str] = ("Arial", 8, "bold")
    font_status: tuple[str, int, str] = ("Arial", 12, "bold")
    font_plane: tuple[str, int, str] = ("Arial", 10, "bold")
    font_alerts: tuple[str, int] = ("Arial", 9)
    font_gallery_info: tuple[str, int] = ("Arial", 8)

    right_panel_width: int = 350
    right_panel_shrink_mid: int = 200
    right_panel_shrink_min: int = 0
    animation_step: int = 15
    animation_interval_ms: int = 16

    statbar_height: int = 20
    statbar_default_width: int = 200
    color_brightness: str = "#00E5FF"
    color_sharpness: str = "#00A0FF"
    color_confidence: str = "#FFFFFF"


@dataclass(frozen=True)
class OverlayConfig:
    """Overlay colors, grid bounds, crosshair markers, and guidelines parameters."""
    primary_color: tuple[int, int, int] = (0, 229, 255)   # Cyan
    secondary_color: tuple[int, int, int] = (0, 165, 255) # Orange
    alert_color: tuple[int, int, int] = (0, 0, 255)       # Red
    text_color: tuple[int, int, int] = (255, 255, 255)
    grid_color: tuple[int, int, int] = (90, 90, 90)
    guidance_color: tuple[int, int, int] = (0, 255, 255)  # Yellow
    locked_color: tuple[int, int, int] = (0, 255, 0)      # Green
    low_conf_color: tuple[int, int, int] = (0, 0, 255)    # Red
    crosshair_color: tuple[int, int, int] = (140, 140, 140)
    scanline_color: tuple[int, int, int] = (40, 40, 40)
    watermark_color: tuple[int, int, int] = (200, 200, 255)

    grid_alpha: float = 0.18
    grid_beta: float = 0.82
    scanline_step: int = 4
    crosshair_marker_size: int = 22
    crosshair_thickness: int = 1

    corner_min_len: int = 15
    corner_max_len: int = 30
    corner_ratio: float = 0.15
    corner_thickness: int = 2

    guidance_margin: int = 40
    stability_bar_width: int = 240
    stability_bar_height: int = 16
    stability_bar_margin_x: int = 30
    stability_bar_margin_y: int = 60

    heatmap_alpha: float = 0.7
    heatmap_beta: float = 0.3
    watermark_text: str = "GENDER DETECTION DISABLED - PC-PNDT COMPLIANT"
    alert_separator: str = "  ???  "


@dataclass(frozen=True)
class OutputConfig:
    """Capture windows, quality constraints, and thumbnail limits configurations."""
    cooldown_time: float = 3.0
    window_duration: float = 2.0
    quality_brightness_weight: float = 0.4
    quality_sharpness_weight: float = 0.6
    quality_brightness_norm: float = 150.0
    quality_sharpness_norm: float = 200.0
    quality_contrast_norm: float = 60.0

    score_confidence_weight: float = 0.5
    score_stability_weight: float = 0.3
    score_quality_weight: float = 0.2

    thumbnail_size: tuple[int, int] = (150, 110)


@dataclass(frozen=True)
class LoggingConfig:
    """Logging destination, layout formats, and parameters."""
    log_file: str = "sono_guide.log"
    log_format: str = "[%(levelname)s] %(asctime)s - %(message)s"


@dataclass(frozen=True)
class RuntimeConfig:
    """Global debug, runtime profile, and execution modes flags."""
    demo_mode: bool = True


@dataclass(frozen=True)
class AppConfig:
    """Consolidated immutable application config container."""
    project: ProjectConfig = ProjectConfig()
    model: ModelConfig = ModelConfig()
    detection: DetectionConfig = DetectionConfig()
    tracking: TrackingConfig = TrackingConfig()
    video: VideoConfig = VideoConfig()
    ui: UIConfig = UIConfig()
    overlay: OverlayConfig = OverlayConfig()
    output: OutputConfig = OutputConfig()
    logging: LoggingConfig = LoggingConfig()
    runtime: RuntimeConfig = RuntimeConfig()


# Single global immutable configuration instance
CONFIG = AppConfig()
