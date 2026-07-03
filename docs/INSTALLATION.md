# Installation Guide

This guide provides instructions to set up the **Sono-Guide** environment on Windows, Linux, and macOS.

---

## 1. Automated Installation (Recommended)

The easiest way to run the application is to use the cross-platform bootstrap launcher, which checks Python versions, creates a virtual environment, installs the required packages, and executes the station in one command.

```bash
python launcher.py
```

---

## 2. Manual Installation

If you prefer to configure your virtual environment manually:

### A. Create the Virtual Environment
Create a virtual environment named `.venv` in the repository root directory:
* **All Platforms**:
  ```bash
  python -m venv .venv
  ```

### B. Activate the Virtual Environment
Activate the environment to isolate the dependencies:
* **Linux/macOS**:
  ```bash
  source .venv/bin/activate
  ```
* **Windows (Command Prompt)**:
  ```cmd
  .venv\Scripts\activate.bat
  ```
* **Windows (PowerShell)**:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

### C. Install CPU-Only PyTorch
Since CUDA/GPU packages are very heavy and not required for desktop inference, install the CPU-only wheels directly from the PyTorch download index:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### D. Install Core and AI Dependencies
Install the remaining required packages from `requirements.txt` and `ultralytics` package:
```bash
pip install -r requirements.txt
pip install ultralytics
```

---

## 3. Platform-Specific Prerequisites

### Linux (Ubuntu/Debian)
Ensure that you have system libraries installed for Tkinter and OpenCV:
```bash
sudo apt update
sudo apt install python3-tk python3-venv libgl1-mesa-glx libglib2.0-0 -y
```

### macOS
For macOS, ensure Xcode Command Line Tools are installed:
```bash
xcode-select --install
```

### Windows
No additional system components are required. Ensure Python is added to your system `PATH` during installation.

---

## 4. Running the Application

### Running with the Launcher
Use the orchestrator launcher to automatically maintain your packages:
```bash
python launcher.py
```
* Use `--skip-install` for fast startup:
  ```bash
  python launcher.py --skip-install
  ```

### Running Standalone
You can launch the main program directly:
```bash
python main.py
```
* **Auto-Handoff**: If run under system Python, `main.py` will search for `.venv/` and re-execute itself inside it, setting up `PYTHONPATH` dynamically.

---

## 5. Common Installation Issues

### OpenCV Import Error (`ImportError: libGL.so.1`)
* **Cause**: Missing OpenGL libraries on Linux headless servers or desktop boxes.
* **Fix**: Install `libgl1-mesa-glx` via `apt`:
  ```bash
  sudo apt install libgl1-mesa-glx -y
  ```

### Python Version Mismatch
* **Cause**: System Python is < 3.10.
* **Fix**: Download and install Python 3.10 or higher from python.org or your system manager.

### Windows Execution Policy Restriction
* **Cause**: PowerShell blocks activation scripts by default.
* **Fix**: Set execution policy to bypass or run launcher:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
