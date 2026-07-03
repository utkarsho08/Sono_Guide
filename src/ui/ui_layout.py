import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from ui.gallery_manager import GalleryManager
from utils.config import CONFIG

class StatBar(tk.Canvas):
    def __init__(self, parent, label, color, **kwargs):
        super().__init__(parent, height=20, bg="#111821", highlightthickness=0, **kwargs)
        self.color = color
        self.label = label
        self.value = 0
        self.draw()

    def set_value(self, val):
        self.value = max(0, min(100, val))
        self.draw()

    def draw(self):
        self.delete("all")
        w = self.winfo_width()
        if w < 10: w = 200 # Default width
        
        # Background
        self.create_rectangle(0, 0, w, 20, fill="#1a242f", outline="")
        # Progress
        fill_w = int(w * (self.value / 100))
        self.create_rectangle(0, 0, fill_w, 20, fill=self.color, outline="")
        # Text
        self.create_text(10, 10, text=f"{self.label}: {int(self.value)}%", 
                         anchor="w", fill="white", font=("Arial", 8, "bold"))

class UILayout:
    def __init__(self, root):
        self.root = root
        self.root.title(CONFIG.ui.title)
        self.root.geometry(CONFIG.ui.geometry)
        self.root.configure(bg=CONFIG.ui.bg_main)

        self._right_panel_width = CONFIG.ui.right_panel_width
        self._panel_phase = 0   # 0=full, 1=shrinking, 2=hidden
        self._anim_target = CONFIG.ui.right_panel_width

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Medical.TFrame", background=CONFIG.ui.bg_main)
        style.configure("Panel.TFrame", background=CONFIG.ui.bg_panel, borderwidth=0)
        style.configure("Header.TFrame", background=CONFIG.ui.bg_main)
        style.configure("Logo.TLabel", background=CONFIG.ui.bg_main, foreground=CONFIG.ui.fg_logo, font=CONFIG.ui.font_logo)
        style.configure("Patient.TLabel", background=CONFIG.ui.bg_main, foreground=CONFIG.ui.fg_white, font=CONFIG.ui.font_patient)
        style.configure("Section.TLabel", background=CONFIG.ui.bg_panel, foreground=CONFIG.ui.fg_logo, font=CONFIG.ui.font_section)

    def create_widgets(self):
        # 1. Patient Header
        self.header = ttk.Frame(self.root, style="Header.TFrame", height=70)
        self.header.pack(side="top", fill="x", padx=20, pady=10)
        self.header.pack_propagate(False)

        ttk.Label(self.header, text="SONO-GUIDE AI", style="Logo.TLabel").pack(side="left", padx=(0, 40))
        
        info_text = "PATIENT ID: SG-2024-001   |   CLINIC: AI DIAGNOSTICS LAB   |   DOB: --/--/--   |   OPERATOR: DEMO MODE"
        ttk.Label(self.header, text=info_text, style="Patient.TLabel").pack(side="left")

        # Main Container
        self.container = ttk.Frame(self.root, style="Medical.TFrame")
        self.container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.container.pack_propagate(False)  # Disable propagation on main container

        # 3. Right Sidebar (Telemetry + Gallery) - Pack first to prioritize its space
        self.right_panel = ttk.Frame(self.container, style="Panel.TFrame", width=CONFIG.ui.right_panel_width)
        self.right_panel.pack(side="right", fill="y")
        self.right_panel.pack_propagate(False)

        # 2. Live Ultrasound Feed (Left) - Pack second to fill remaining space
        self.left_panel = ttk.Frame(self.container, style="Panel.TFrame")
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.left_panel.pack_propagate(False)  # Disable propagation on left panel

        # Feed Container - intermediate frame to isolate feed_label geometry
        self.feed_container = ttk.Frame(self.left_panel, style="Panel.TFrame")
        self.feed_container.pack(fill="both", expand=True)
        self.feed_container.pack_propagate(False)  # Disable propagation on feed container
        
        self.feed_label = tk.Label(self.feed_container, bg="#000000", bd=2, relief="flat")
        self.feed_label.pack(fill="both", expand=True, padx=2, pady=2)

        # Telemetry
        tel_frame = ttk.Frame(self.right_panel, style="Panel.TFrame")
        tel_frame.pack(fill="x", padx=20, pady=20)
        ttk.Label(tel_frame, text="DIAGNOSTIC TELEMETRY", style="Section.TLabel").pack(anchor="w", pady=(0, 15))

        self.bars = {
            'brightness': StatBar(tel_frame, "BRIGHTNESS", CONFIG.ui.color_brightness),
            'sharpness': StatBar(tel_frame, "SHARPNESS", CONFIG.ui.color_sharpness),
            'confidence': StatBar(tel_frame, "CONFIDENCE", CONFIG.ui.color_confidence)
        }
        for bar in self.bars.values():
            bar.pack(fill="x", pady=5)

        # AI Status Message
        self.ai_status_label = ttk.Label(self.right_panel, text="INITIALIZING...", 
                                        foreground=CONFIG.ui.fg_logo, background=CONFIG.ui.bg_panel, font=CONFIG.ui.font_status)
        self.ai_status_label.pack(pady=10)

        # Standard Plane label
        self.plane_label = ttk.Label(self.right_panel, text="", 
                                     foreground=CONFIG.ui.fg_orange, background=CONFIG.ui.bg_panel, font=CONFIG.ui.font_plane,
                                     wraplength=300)
        self.plane_label.pack(anchor="w", padx=20)

        # Gallery
        ttk.Label(self.right_panel, text="CAPTURED PLANES", style="Section.TLabel").pack(anchor="w", padx=20, pady=(20, 10))
        self.gallery_frame = ttk.Frame(self.right_panel, style="Panel.TFrame")
        self.gallery_frame.pack(fill="both", expand=True, padx=10)
        self.gallery = GalleryManager(self.gallery_frame)

        # Alerts (Bottom small)
        self.alerts_text = tk.Text(self.right_panel, bg="#111821", fg="#ff3333", height=4, font=("Arial", 9), bd=0)
        self.alerts_text.pack(fill="x", side="bottom", padx=20, pady=20)

    # ── Animated panel expand/shrink ─────────────────────────────────────────
    def expand_feed(self, phase):
        """
        phase 0 → right panel full (350px)
        phase 1 → right panel shrinking (200px)
        phase 2 → right panel hidden (0px)
        """
        targets = {
            0: CONFIG.ui.right_panel_width,
            1: CONFIG.ui.right_panel_shrink_mid,
            2: CONFIG.ui.right_panel_shrink_min
        }
        target = targets.get(phase, CONFIG.ui.right_panel_width)
        if self._panel_phase != phase:
            self._panel_phase = phase
            self._animate_panel(target)

    def _animate_panel(self, target_width, step=CONFIG.ui.animation_step):
        current = self._right_panel_width
        if current == target_width:
            return
        direction = 1 if target_width > current else -1
        new_width = current + direction * step
        if (direction > 0 and new_width >= target_width) or \
           (direction < 0 and new_width <= target_width):
            new_width = target_width

        self._right_panel_width = new_width

        if new_width <= 0:
            self.right_panel.pack_forget()
        else:
            try:
                # Pack before left_panel to maintain packing layout order priority
                self.right_panel.pack(side="right", fill="y", before=self.left_panel)
            except Exception:
                self.right_panel.pack(side="right", fill="y")
            self.right_panel.configure(width=new_width)

        if new_width != target_width:
            self.root.after(16, self._animate_panel, target_width, step)

    def update_telemetry(self, brightness, sharpness, confidence, stability):
        # Scale values to 0-100 for bars
        self.bars['brightness'].set_value(brightness * 100 / 255)
        self.bars['sharpness'].set_value(min(100, sharpness / 5)) # Normalizing sharpness
        self.bars['confidence'].set_value(confidence * 100)

    def update_alerts(self, alerts):
        self.alerts_text.delete('1.0', tk.END)
        if alerts:
            for alert in alerts:
                self.alerts_text.insert(tk.END, f"[-] {alert}\n")
        else:
            self.alerts_text.insert(tk.END, "[+] SYSTEMS NOMINAL\n")

    def flash_screen(self):
        def reset_color():
            self.feed_label.config(highlightbackground="black")
        self.feed_label.config(highlightbackground="white", highlightthickness=4)
        self.root.after(150, reset_color)
