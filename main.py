
import sys
from pathlib import Path

import tkinter as tk

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from ui.ui_layout import UILayout
from video.video_engine import VideoEngine
from utils.paths import DEFAULT_VIDEO


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
