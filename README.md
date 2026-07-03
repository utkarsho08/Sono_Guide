# Sono-Guide

AI-assisted ultrasound plane detection demo application.

## Requirements

- Python 3.8+
- Tkinter (usually included with Python)

## Dependency Strategy

Dependencies are split into lightweight runtime packages and a separate heavy AI
stack. This keeps setup fast and cross-platform friendly.

| Group        | File                         | Packages                          |
|--------------|------------------------------|-----------------------------------|
| Lightweight  | `requirements.txt`           | numpy, opencv-python, pillow      |
| Heavy AI     | `requirements/ai.txt`        | torch, torchvision, ultralytics   |
| Optional     | `requirements/optional.txt`  | matplotlib, pandas, scipy         |
| Development  | `requirements/dev.txt`       | pytest, ruff, black, mypy         |

Full details: [docs/DEPENDENCY_PLAN.md](docs/DEPENDENCY_PLAN.md)

## Recommended Setup (Cross-Platform Launcher)

The launcher creates a virtual environment, installs only missing CPU-only
dependencies, and runs the app:

```bash
python launcher.py
```

Install stages:

```text
1. python -m pip install --upgrade pip
2. python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
3. python -m pip install -r requirements/ai.txt
4. python -m pip install -r requirements.txt
5. python main.py
```

Launcher options:

```bash
python launcher.py --install-only     # install dependencies only
python launcher.py --skip-install     # run without installing
python launcher.py --show-plan        # print install stages
```

## Manual Run (Dependencies Already Installed)

```bash
python main.py
```

## Project Layout

```text
├── main.py                   # Application entry point
├── launcher.py               # Cross-platform bootstrap + launcher
├── requirements.txt          # Lightweight dependencies only
├── requirements/
│   ├── ai.txt                # Heavy AI dependencies
│   ├── optional.txt
│   └── dev.txt
├── setup/
│   └── dependencies.py     # Dependency metadata for launcher
├── assets/
│   ├── models/               # YOLO model weights
│   ├── images/               # Demo video files
│   └── icons/
├── src/
│   ├── ai/                   # AI detection (YOLO) — heavy deps isolated here
│   ├── tracking/             # Stability / motion tracking
│   ├── ui/                   # Tkinter UI
│   ├── video/                # Video engine, overlays, capture
│   └── utils/                # Shared utilities and paths
├── docs/
│   └── DEPENDENCY_PLAN.md
├── logs/
└── output/                   # Auto-captured frame images
```

## License

See [LICENSE](LICENSE).
