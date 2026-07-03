# Dependency Guide

This guide details the dependency management structure, manifest breakdown, and bootstrap installation logic in **Sono-Guide**.

---

## 1. Why Dependencies are Separated

Traditional Python projects list all packages in a single `requirements.txt`. For projects with AI dependencies (like PyTorch and Ultralytics), this causes several issues:
1. **Pipelining Bloat**: A single file forces the installation of multiple gigabytes of CUDA packages, even on lightweight CPU-only desktop clients.
2. **Setup Failures**: Mixing platform-specific PyTorch dependencies with general packages often breaks pip resolver logic on Windows, Linux, and macOS.
3. **Usability**: Separating base packages from heavy modules allows developer-only dependencies (or optional enhancements) to remain isolated.

---

## 2. Dependency Layout

Sono-Guide segments package specifications into four target manifests:

### A. `requirements.txt` (Core Runtime)
Contains base packages required for image loading, matrix operations, and video ingestion:
* **`opencv-python`**: OpenCV framework for image filtering.
* **`numpy`**: Fast matrix computation.
* **`pillow`**: Image handling and conversion for Tkinter display.

### B. `requirements/ai.txt` (Heavy Inference)
Contains deep learning libraries:
* **`torch` / `torchvision`**: PyTorch CPU-optimized inference backend.
* **`ultralytics`**: YOLOv8 neural network wrapper.
* **`--extra-index-url https://download.pytorch.org/whl/cpu`**: Resolves CPU-only wheel packages to avoid CUDA package bloat.

### C. `requirements/dev.txt` (Developer Auditing)
Contains analysis utilities for code hygiene, formatting, and typing:
* **`flake8`**: Standard code linter.
* **`black`**: Code formatter.
* **`mypy`**: Static type checker.

### D. `requirements/optional.txt` (Optional Extras)
Contains optional tools for performance benchmarking or system checks.

---

## 3. CPU-Only PyTorch Optimization

Installing PyTorch standard packages fetches CUDA-enabled libraries, which can exceed **2GB** in download size and require matching Nvidia graphics card drivers. 

Sono-Guide solves this by instructing pip to fetch from the official PyTorch CPU wheel directory:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```
This reduces the download size to **~350MB**, allows installation on hardware without GPUs, and prevents driver version crashes.

---

## 4. How the Launcher Installs Packages

The orchestrator in `setup/dependency_manager.py` verifies and installs packages in a strict sequence:

```text
[Check Python Version] ──> [Create .venv] ──> [Upgrade pip]
                                                   │
                                                   v
[Verify Core & Dev Packages] <── [Install Ultralytics] <── [Install PyTorch CPU]
             │
             v
 [Verify Model Assets] ──> [Launch main.py]
```

1. **Verification**: Queries packages using Python `importlib.metadata` and `importlib.util.find_spec`. If all dependencies are satisfied, it skips installer execution for a fast offline boot.
2. **Order-Sensitive Installs**:
   * Upgrades `pip` to ensure robust package resolution.
   * Installs `torch` and `torchvision` from the PyTorch CPU wheel registry.
   * Installs `ultralytics`.
   * Installs the core packages list.
   * (If dev mode is active) Installs the development auditing tools.
