# Sono-Guide Dependency Plan

This document defines how dependencies are split, installed, and managed for
cross-platform CPU-only deployment.

## Design Goals

- Keep `requirements.txt` limited to lightweight Python packages.
- Isolate heavy AI dependencies from the core application requirements.
- Install CPU-only PyTorch wheels (never CUDA/GPU builds).
- Support a single cross-platform launcher that creates a venv, installs only
  missing packages, and runs `main.py`.

## Install Order (Automated by `launcher.py`)

```text
1. python -m pip install --upgrade pip
2. python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
3. python -m pip install -r requirements/ai.txt
4. python -m pip install -r requirements.txt
5. python main.py
```

## Dependency Groups

### Lightweight Dependencies

Installed from `requirements.txt` after the AI stack.

| Package        | Import | Used By                                      |
|----------------|--------|----------------------------------------------|
| numpy          | numpy  | AI, video, tracking, utils                   |
| opencv-python  | cv2    | AI, video, tracking, utils                   |
| pillow         | PIL    | UI, video engine                             |

Stdlib packages also used: `tkinter`, `threading`, `pathlib`, `datetime`, etc.

### Heavy AI Dependencies

Installed separately; **must not** appear in `requirements.txt`.

| Package     | Install Source                                      | Used By        |
|-------------|-----------------------------------------------------|----------------|
| torch       | `requirements/ai.txt` (CPU index)                   | ultralytics    |
| torchvision | `requirements/ai.txt` (CPU index)                   | ultralytics    |
| ultralytics | `requirements/ai.txt`                               | `src/ai/`      |

Code boundary: all Ultralytics/YOLO usage lives under `src/ai/`.

### Optional Dependencies

Listed in `requirements/optional.txt`. Not installed by the launcher.

| Package    | Notes                                      |
|------------|--------------------------------------------|
| matplotlib | Plotting / analytics extensions            |
| pandas     | Tabular data workflows                     |
| scipy      | Scientific computing extensions            |

Install manually when needed:

```bash
python -m pip install -r requirements/optional.txt
```

### Development Dependencies

Listed in `requirements/dev.txt`. Not installed by the launcher.

| Package | Purpose                 |
|---------|-------------------------|
| pytest  | Automated testing       |
| ruff    | Linting / formatting    |
| black   | Code formatting style   |
| mypy    | Static type checking    |

Install manually for local development:

```bash
python -m pip install -r requirements/dev.txt
```

## File Layout

```text
requirements.txt              # Lightweight runtime packages only
requirements/
  ai.txt                      # Ultralytics (heavy AI)
  optional.txt                # Optional analytics/science packages
  dev.txt                     # Development tooling
setup/
  dependencies.py             # Install metadata and package group definitions
src/ai/
  deps.py                     # AI dependency boundary documentation
launcher.py                   # Cross-platform bootstrap + app launcher
```

## Rules

1. **Never** add `torch`, `torchvision`, `torchaudio`, or `ultralytics` to
   `requirements.txt`.
2. **Never** use CUDA-enabled PyTorch builds in automated setup.
3. **Never** install GPU-specific dependencies automatically.
4. PyTorch and Ultralytics remain required for YOLO inference; only their
   installation path is optimized.
5. The launcher installs only missing packages by default (`--force-reinstall`
   overrides this behavior).

## Manual Setup (Without Launcher)

For developers who prefer manual installation:

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

python -m pip install --upgrade pip
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements/ai.txt
python -m pip install -r requirements.txt
python main.py
```

## Future Launcher Usage

```bash
python launcher.py                 # install missing deps + run app
python launcher.py --install-only  # install only
python launcher.py --skip-install  # run only (deps must already exist)
python launcher.py --show-plan     # print install stages
```
