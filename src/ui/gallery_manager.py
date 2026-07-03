import tkinter as tk
from PIL import Image, ImageTk

class GalleryManager:
    def __init__(self, master_frame):
        self.master_frame = master_frame
        self.captures = []
        
        # Scrollable gallery setup
        self.canvas = tk.Canvas(master_frame, bg="#1a1a1a", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(master_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#1a1a1a")

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

    def add_capture(self, capture_data):
        self.captures.append(capture_data)
        
        # Create thumbnail
        img = Image.open(capture_data['path'])
        img.thumbnail((150, 110))
        photo = ImageTk.PhotoImage(img)

        # Thumbnail Container
        frame = tk.Frame(self.scrollable_frame, bg="#2d2d2d", bd=1, relief="ridge")
        frame.pack(pady=5, padx=5, fill="x")

        label_img = tk.Label(frame, image=photo, bg="#2d2d2d")
        label_img.image = photo # Keep reference
        label_img.pack()

        label_info = tk.Label(frame, text=f"{capture_data['timestamp']}\n{capture_data['label']}", 
                             fg="#ffffff", bg="#2d2d2d", font=("Arial", 8))
        label_info.pack(pady=2)
        
        # Scroll to bottom
        self.canvas.yview_moveto(1.0)
