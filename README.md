# Sono-Guide: Professional AI Ultrasound Station

## 1. Overview
Sono-Guide is an AI-assisted ultrasound guidance station designed to assist clinical operators in standard plane identification, quality assessment, and auto-capturing during ultrasound scans. Equipped with YOLO-based standard plane detection, real-time Farneback optical flow tracking, image calibration warning systems, and diagnostic telemetry dashboards, Sono-Guide brings intelligent verification to medical imaging workflows.

## 2. Features
* **AI-Assisted Plane Detection**: Real-time identification of standard fetal planes (Head BPD, Abdomen AC, Femur FL) using YOLO and classical region proposals.
* **Probe Stability Tracker**: Calculates motion thresholds using optical flow to verify probe stabilization and lock target frames.
* **Auto-Freeze & Capture**: Automatically captures high-quality stable frames, scores them based on confidence and quality, and saves them to the gallery database.
* **Calibration Warning System**: Monitors image gain (low/high), focus sharpness, contrast limits, and speckle noise level in real-time.
* **Centralized Configuration**: All thresholds, styles, colors, and timing parameters are centralized in a frozen, read-only configuration class.
* **Decoupled Bootstrapper**: Separation of setup stages allows simple launcher execution across Windows, Linux, and macOS.

## 3. Project Architecture
Sono-Guide is designed with a decoupled architecture that separates configuration, dependency management, GUI layout, and runtime engines:

```text
               +--------------------------------------+
               |             launcher.py              |  <-- Bootstrapper Entry
               +-------------------+------------------+
                                   |
                                   v
               +--------------------------------------+
               |             setup/                   |  <-- Venv & Packages Auditor
               +-------------------+------------------+
                                   |
                                   v
               +--------------------------------------+
               |               main.py                |  <-- App Entrance (Venv Handoff)
               +-------------------+------------------+
                                   |
                                   v
               +-------------------+------------------+
               |                 src/                 |
               +--------------------------------------+
                 /                 |                \
                /                  |                 \
  +------------+             +-----------+             +------------+
  |    ui/     |             |  utils/   |             |   video/   |
  +------------+             +-----------+             +------------+
  | Layout,    |             | config.py |             | Video &    |
  | Gallery    |             | paths.py  |             | Overlay    |
  | telemetry  |             | utils.py  |             | Engines    |
  +------------+             +-----------+             +------------+
        ^                          ^                         ^
        |                          |                         |
        +--------------------------+-------------------------+
                                   |
                                   v
                             +-----------+
                             |    ai/    |  <-- YOLO / Kalman Filter
                             +-----------+
```

## 4. Directory Structure
```text
SONO_GUIDE/
├── assets/                     # Model weights and test media assets
│   ├── icons/                  # Interface icons
│   ├── images/                 # Default demo video clips
│   └── models/                 # YOLO best.pt weights
├── docs/                       # Comprehensive project documentation
├── logs/                       # Application runtime log files
├── output/                     # Auto-frozen captured images database
├── requirements/               # Modular dependency manifests
│   ├── ai.txt                  # Heavy PyTorch + Ultralytics packages
│   ├── dev.txt                 # Quality checkers and formatter packages
│   └── optional.txt            # Optional extras
├── setup/                      # Decoupled launch orchestration scripts
│   ├── bootstrap.py            # Model verifier and subprocess runner
│   ├── dependencies.py         # Dynamic manifest package parser
│   ├── dependency_manager.py   # Pip upgrade and wheel installer
│   ├── python_checker.py       # Compiler version validator
│   └── venv_manager.py         # Platform-specific virtual env creator
├── src/                        # Core source codebase
│   ├── ai/                     # YOLO and Kalman tracking modules
│   ├── tracking/               # Farneback optical flow stability modules
│   ├── ui/                     # Tkinter layout, telemetry, and gallery
│   ├── utils/                  # Central config, paths, and OS utilities
│   └── video/                  # Calibration, overlays, and main engines
├── CHANGELOG.md                # Version release records
├── launcher.py                 # Thin bootstrapper entry point
├── main.py                     # Standalone script entry point
└── requirements.txt            # Core lightweight dependencies
```

## 5. Installation
To run Sono-Guide, ensure Python 3.10 or higher is installed. The repository includes an automated cross-platform bootstrapper that configures the environment and installs all dependencies inside an isolated virtual environment (`.venv`).

Clone the repository:
```bash
git clone https://github.com/utkarsho08/Sono_Guide.git
cd Sono_Guide
```

## 6. Quick Start
Run the project bootstrapper to automatically configure the virtual environment, install PyTorch CPU, Ultralytics, OpenCV, and launch the application:
```bash
python launcher.py
```

## 7. Manual Setup
If you prefer to configure the environment manually:
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the virtual environment:
   * **Linux/macOS**: `source .venv/bin/activate`
   * **Windows (CMD)**: `.venv\Scripts\activate.bat`
   * **Windows (PowerShell)**: `.venv\Scripts\Activate.ps1`
3. Install PyTorch CPU and components from PyTorch index:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
   ```
4. Install remaining core dependencies:
   ```bash
   pip install -r requirements.txt
   pip install ultralytics
   ```

## 8. Launcher Usage
The `launcher.py` script supports several CLI parameters to control the startup phases:
* **Upgrade and run**: `python launcher.py`
* **Skip dependency audits**: `python launcher.py --skip-install` (Fast offline startup)
* **Install only**: `python launcher.py --install-only` (Pre-install requirements and exit)
* **Developer setup**: `python launcher.py --dev` (Installs development dependencies)
* **View bootstrapper plan**: `python launcher.py --show-plan`

## 9. Running without Launcher
You can execute the application directly without the launcher:
```bash
python main.py
```
* **Venv Auto-Handoff**: If run under system Python, `main.py` will automatically re-execute itself using the local virtual environment `.venv` interpreter (if present) and set up the `PYTHONPATH` correctly.
* **Friendly Warnings**: If the virtual environment has not been initialized, it will gracefully exit with clear configuration instructions instead of showing raw stack tracebacks.

## 10. Requirements
* **Operating System**: Windows 10/11, Ubuntu 20.04+, or macOS Catalina+
* **Python Version**: >= 3.10
* **Disk Space**: ~2GB (includes YOLO weight models and dependencies)

## 11. Dependency Layout
Dependencies are split into targeted manifests to separate lightweight runtime components from heavy AI libraries:
* **`requirements.txt`**: Base packages (`opencv-python`, `numpy`, `pillow`) required for basic execution.
* **`requirements/ai.txt`**: Heavy packages (`torch`, `torchvision`, `ultralytics`) required for AI inference.
* **`requirements/dev.txt`**: Tooling packages (`flake8`, `mypy`, `black`, `isort`) for development audits.

## 12. Configuration
All system-wide configurations are centralized inside `src/utils/config.py` in immutable dataclass structures:
* **Detection Config**: Confidence targets, Kalman noise covariance, Canny thresholds, and anatomical plane labels.
* **Tracking Config**: Optical flow motion limits and stability lock counts.
* **UI Config**: Layout coordinates, color themes, font specifications, and animation speeds.
* **Overlay Config**: HUD crosshair dimensions, diagnostic grids, and compliance watermarks.
* **Output Config**: Capture window timers, quality metrics, and thumbnail limits.

## 13. Screenshots
*(Placeholder image for main dashboard layout view)*
![Dashboard Layout Mockup](https://raw.githubusercontent.com/utkarsho08/Sono_Guide/main/assets/images/dashboard_placeholder.png)

## 14. Troubleshooting
* **Missing `cv2` or `torch`**: Ensure you run `python launcher.py` to compile the virtual environment and fetch the wheels.
* **YOLO best.pt Not Found**: Place the model weights inside `assets/models/best.pt`.
* For platform-specific errors, refer to [docs/TROUBLESHOOTING.md](file:///home/utkarsh/Documents/uhack4.0/SONO_GUIDE/docs/TROUBLESHOOTING.md).

## 15. FAQ
* **Does it require a CUDA GPU?** No, the installation is optimized for CPU-only execution, making it compatible with lightweight laptops.
* **How are frames stored?** Captures are saved as JPEGs inside the `output/` directory, named with microsecond-accurate timestamps.

## 16. Future Improvements
* Add GPU/CUDA detection to automatically install PyTorch GPU wheels when graphics cards are present.
* Support real-time video feed ingestion from local capture cards or webcams.

## 17. Contributing
Please refer to [docs/DEVELOPER_GUIDE.md](file:///home/utkarsh/Documents/uhack4.0/SONO_GUIDE/docs/DEVELOPER_GUIDE.md) for style guides, typing instructions, and branch workflows.

## 18. License
This project is licensed under the MIT License - see the [LICENSE](file:///home/utkarsh/Documents/uhack4.0/SONO_GUIDE/LICENSE) file for details.

## 19. Authors
* **Utkarsh** - Lead Architecture and Core Development (GitHub: [@utkarsho08](https://github.com/utkarsho08))
