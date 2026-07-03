import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe" if os.name == "nt" else ROOT / ".venv" / "bin" / "python"

# Re-execute main.py inside the virtual environment if running standalone with system python
if VENV_PYTHON.is_file() and Path(sys.executable).resolve() != VENV_PYTHON.resolve():
    env = os.environ.copy()
    src_dir = str(ROOT / "src")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src_dir if not existing_pythonpath else f"{src_dir}{os.pathsep}{existing_pythonpath}"
    
    cmd = [str(VENV_PYTHON), __file__] + sys.argv[1:]
    try:
        sys.exit(subprocess.run(cmd, env=env).returncode)
    except Exception as e:
        print(f"[ERROR] Failed to launch virtual environment: {e}", file=sys.stderr)
        sys.exit(1)
elif not VENV_PYTHON.is_file():
    print("[WARNING] Virtual environment not found. Run 'python launcher.py' to initialize.", file=sys.stderr)

sys.path.insert(0, str(ROOT / "src"))


try:
    import tkinter as tk
    from ui.ui_layout import UILayout
    from video.video_engine import VideoEngine
    from utils.paths import DEFAULT_VIDEO
except ImportError as e:
    print(f"[ERROR] Failed to import dependencies: {e}", file=sys.stderr)
    print("[ERROR] Please initialize the virtual environment by running 'python launcher.py'.", file=sys.stderr)
    sys.exit(1)


def main():

    # Create main window
    root = tk.Tk()
    root.title("AI Assisted Ultrasound Plane Detection")
    root.geometry("1200x800")
    root.minsize(900, 600)

    # Initialize UI
    ui = UILayout(root)

    # Initialize Video Engine
    engine = VideoEngine(ui, video_path=str(DEFAULT_VIDEO))

    # Link engine to UI (useful if UI buttons need engine access later)
    ui.engine = engine

    # Graceful shutdown
    def on_closing():
        try:
            engine.stop()
        except Exception:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start video processing
    engine.start()

    # Start UI loop
    root.mainloop()


if __name__ == "__main__":
    main()
