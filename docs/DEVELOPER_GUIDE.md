# Developer Guide

This guide provides guidelines and best practices for developers contributing to the **Sono-Guide** project.

---

## 1. Coding Conventions

* **PEP 8 Compliance**: Follow standard Python conventions. All code should pass style audits.
* **Type Annotations**: Provide explicit type hints for all public classes, method parameters, and return values. Avoid over-annotating internal local variables.
* **Imports Ordering**: Group imports in order, separated by a blank line:
  1. Standard Library
  2. Third-party Libraries
  3. Project Modules
  * Avoid wildcard imports (`from module import *`).
* **Exceptions**: Catch specific exceptions (e.g. `OSError`, `RuntimeError`) rather than generic `Exception` or bare `except:`.

---

## 2. Centralized Configuration

All global settings must be placed in `src/utils/config.py`.

### How to Add Configuration Entries
1. Locate the appropriate configuration class (e.g. `DetectionConfig`, `VideoConfig`).
2. Add your variable with appropriate type annotations and a default value:
   ```python
   @dataclass(frozen=True)
   class DetectionConfig:
       ...
       new_parameter: float = 0.75
   ```
3. Reference this value anywhere in the source code using the global `CONFIG` instance:
   ```python
   from utils.config import CONFIG
   # Usage:
   threshold = CONFIG.detection.new_parameter
   ```

---

## 3. Managing Dependencies

Dependencies must not be hardcoded in installation scripts.

### How to Add a Dependency
1. Select the correct requirements manifest:
   * **`requirements.txt`**: Base packages required for basic CPU runtime (e.g. `numpy`, `pillow`).
   * **`requirements/ai.txt`**: Heavy modules for AI inference (e.g. `torch`, `ultralytics`).
   * **`requirements/dev.txt`**: Tools for testing, formatting, and analysis.
2. Add the package (with version bounds) to the selected text file.
3. The dependency auditor in `setup/dependencies.py` will automatically parse the requirements list on the next launch:
   ```python
   # Packages are dynamically loaded at runtime
   LIGHTWEIGHT_DEPENDENCIES = tuple(_parse_manifest(REQUIREMENTS_LIGHTWEIGHT))
   ```

---

## 4. Creating a New Module

When adding new functionality to `src/`:
1. Ensure the module is created under a logical subfolder (e.g. `src/ai/`, `src/video/`).
2. If it is a public class, expose it inside the package's `__init__.py` file:
   ```python
   from .my_module import MyClass
   __all__ = ["MyClass"]
   ```
3. Use relative imports for siblings inside the same subpackage, and absolute imports from `src/` root for other components.

---

## 5. Logging Guidelines

All logs should write output to the unified log location.
* Use the Python `logging` module to direct outputs to `logs/sono_guide.log`.
* Do **NOT** use `print()` statements for internal telemetry or debug logs.
* Ensure clear log prefixes indicating the originating module (e.g. `[AI_DETECTOR]`, `[VIDEO_ENGINE]`).

---

## 6. Testing Philosophy

* **Static Verification**: Always run compilation checks and lint audits (`flake8`, `mypy`) before staging changes:
  ```bash
  python -m py_compile main.py
  ```
* **No Runtime Mocking**: Since the core calibration and AI engines are visual, verify frame updates manually using simulated noise frames if no capture hardware is present.
