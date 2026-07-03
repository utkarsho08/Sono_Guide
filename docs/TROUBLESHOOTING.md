# Troubleshooting Guide

This guide provides solutions to common issues encountered when setting up, launching, or running **Sono-Guide**.

---

## 1. Dependency Issues

### Missing `cv2`
* **Error**: `ModuleNotFoundError: No module named 'cv2'`
* **Cause**: OpenCV is not installed, or you are running the project outside the virtual environment.
* **Fix**:
  * Run the project using the orchestrator: `python launcher.py`.
  * If running standalone, make sure the virtual environment is activated: `source .venv/bin/activate` (or platform equivalent).
  * On Linux (headless/minimal systems), you may also need to install the system OpenGL libraries:
    ```bash
    sudo apt install libgl1-mesa-glx libglib2.0-0 -y
    ```

### Missing `torch` or `ultralytics`
* **Error**: `ModuleNotFoundError: No module named 'torch'` or `No module named 'ultralytics'`
* **Cause**: Deep learning dependencies were not installed successfully.
* **Fix**:
  * Force the launcher to audit and install packages:
    ```bash
    python launcher.py
    ```
  * Or install them manually inside the activated virtual environment:
    ```bash
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    pip install ultralytics
    ```

---

## 2. Asset & Model Issues

### Missing YOLO Weights or Test Video
* **Error**: `[ERROR] Missing critical assets or model files: Model file missing: assets/models/best.pt`
* **Cause**: The YOLO model weights file is missing.
* **Fix**:
  * Download your trained YOLOv8 model weights file (usually `best.pt` or `yolov8n.pt`).
  * Create the directory structure `assets/models/` and place the file inside it.
  * Verify that the demo video asset is placed inside `assets/images/ultrasound_demo.mp4`.

---

## 3. Launcher & Virtual Environment Issues

### Virtual Environment Fails to Create
* **Error**: `[ERROR] Failed to create virtual environment`
* **Cause**: Python `venv` library is missing or restricted.
* **Fix**:
  * On Debian/Ubuntu Linux systems, the Python venv module is packaged separately. Install it using:
    ```bash
    sudo apt install python3-venv -y
    ```

### Python Version Mismatch
* **Error**: `[ERROR] Unsupported Python version. Sono-Guide requires Python 3.10 or higher.`
* **Cause**: The default `python` command points to an older version (e.g. Python 3.8).
* **Fix**:
  * Check the version using: `python --version`.
  * Install Python 3.10 or higher.
  * Explicitly run the launcher using the newer python binary:
    ```bash
    python3 launcher.py
    ```

---

## 4. Platform-Specific Issues

### Windows: PowerShell Execution Policy Restriction
* **Error**: `.venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system.`
* **Cause**: Windows PowerShell restricts script execution by default.
* **Fix**:
  * Run PowerShell as Administrator and enable script execution for the local process:
    ```powershell
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    ```
  * Or run the launcher script using CMD instead of PowerShell.

### Linux: Permission Denied on Output
* **Error**: `PermissionError: [Errno 13] Permission denied` when saving captures.
* **Cause**: Write permissions are missing on the project root or the `output/` directory.
* **Fix**:
  * Change ownership or grant write permission to the output folder:
    ```bash
    chmod -R 775 output/
    ```

### macOS: Gatekeeper or Binary Security Warnings
* **Error**: Warnings block execution of compiled NumPy or PyTorch binaries.
* **Cause**: macOS Gatekeeper restricts unsigned binaries.
* **Fix**:
  * Allow terminal applications in System Settings → Privacy & Security.
  * If needed, clear security quarantine attributes on the `.venv` folder:
    ```bash
    xargs xattr -r -d com.apple.quarantine .venv/
    ```
