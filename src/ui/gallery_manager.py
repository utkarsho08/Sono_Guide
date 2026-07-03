import tkinter as tk
from PIL import Image, ImageTk

from utils.config import CONFIG


class GalleryManager:
    """Manages the scrollable image gallery UI for capturing standard planes."""

    def __init__(self, master_frame: tk.Frame) -> None:
        self.master_frame = master_frame
        self.captures: list[dict] = []
        
        # Scrollable gallery setup
        self.canvas = tk.Canvas(master_frame, bg=CONFIG.ui.bg_canvas, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(master_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=CONFIG.ui.bg_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def add_capture(self, capture_data: dict) -> None:
        """Add a captured plane image to the scrollable sidebar gallery."""
        self.captures.append(capture_data)
        
        # Create thumbnail
        img = Image.open(capture_data['path'])
        img.thumbnail(CONFIG.output.thumbnail_size)
        photo = ImageTk.PhotoImage(img)

        # Thumbnail Container
        frame = tk.Frame(self.scrollable_frame, bg=CONFIG.ui.bg_thumbnail_container, bd=1, relief="ridge")
        frame.pack(pady=5, padx=5, fill="x")

        label_img = tk.Label(frame, image=photo, bg=CONFIG.ui.bg_thumbnail_container)
        label_img.image = photo # Keep reference
        label_img.pack()

        label_info = tk.Label(frame, text=f"{capture_data['timestamp']}\n{capture_data['label']}", 
                             fg=CONFIG.ui.fg_white, bg=CONFIG.ui.bg_thumbnail_container, font=CONFIG.ui.font_gallery_info)
        label_info.pack(pady=2)
        
        # Scroll to bottom
        self.canvas.yview_moveto(1.0)
