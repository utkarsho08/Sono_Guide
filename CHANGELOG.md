# Changelog

All notable changes to the **Sono-Guide** project will be documented in this file.

---

## [v1.0.0] - 2026-07-04

This release marks the first stable, production-quality release of the **Sono-Guide** AI Ultrasound Guidance Station, following a comprehensive architecture audit, configuration centralization, and functional stabilization.

### Summary of Changes

#### 1. Architecture Redesign & Folder Structure
* **Layout Separation**: Reorganized files into structured folders (`src/`, `setup/`, `assets/`, `docs/`, `logs/`, `output/`).
* **Path Management**: Eliminated hardcoded directories and replaced legacy `os.path` operations with unified cross-platform `pathlib.Path` structures.
* **acyclic Import Structure**: Audited code imports to verify static resolution, preventing circular imports.

#### 2. Cross-Platform Orchestrator Launcher
* **Modular Launcher**: Redesigned `launcher.py` into a thin shell runner.
* **Separation of Setup**: Created specialized setup submodules under `setup/` to isolate version validation (`python_checker.py`), environment creation (`venv_manager.py`), and subprocess execution (`bootstrap.py`).

#### 3. Single Source of Truth Dependency Management
* **Dynamic Manifest Parser**: Updated `setup/dependencies.py` to dynamically parse dependency packages and PyTorch index URLs directly from files (`requirements.txt`, `requirements/ai.txt`).
* **Isolation of Heavy AI Packages**: Moved `torch`, `torchvision`, and `ultralytics` to `requirements/ai.txt` to avoid package bloat. Optimized for CPU-only PyTorch download weights (~350MB instead of 2GB+).

#### 4. Centralized Configuration System
* **Global Immutable Config**: Added a frozen config object `CONFIG` in `src/utils/config.py`.
* **Namespace Isolation**: Grouped variables into distinct sections (e.g. `CONFIG.ui`, `CONFIG.video`, `CONFIG.overlay`, `CONFIG.detection`).
* **Magic Numbers Eliminated**: Mapped GUI geometry, styling colors, font values, frame timing delays, Canny limits, and Kalman values to configuration fields.

#### 5. Functional & UI Layout Stabilization
* **Cumulative Expansion Bug Fixed**: Fixed positive feedback loop that compressed the right panel by disabling packing propagation (`pack_propagate(False)`) on `left_panel` and the new `feed_container`.
* **Cavity Allocation Priority**: Re-ordered widget packing to ensure the right sidebar is packed first, preserving its width during slides.
* **Aspect-Ratio-Preserved Resizing**: Replaced direct stretching of image frames with aspect-ratio-locked scaling, centering videos cleanly with black bars.
* **Standalone Launch Handoff**: Added automatic redirection in `main.py` to re-execute itself inside `.venv` and friendly interceptions of missing package errors.

#### 6. Code Quality Improvements
* **PEP 8 Compliance**: Re-ordered import statements, removed unused imports, and eliminated wildcard imports.
* **Type Annotations**: Equipment methods and parameters with explicit type hints.
* **Docstrings**: Added brief docstrings to public classes and routines.
* **Exception Auditing**: Replaced general `except:` blocks with specific exception types.
* **Dead Code Cleanup**: Removed unused variables and dead references.

### Known Issues
* **resizing workload**: Calling `Image.resize` with `Resampling.LANCZOS` at 30 FPS can be CPU-intensive on low-spec systems. Can be switched to bilinear in config if needed.
