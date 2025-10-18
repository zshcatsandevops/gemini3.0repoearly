import tkinter as tk
from tkinter import font

# Main Application Class
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Xbox 360 Controller Render")
        self.geometry("600x620")
        self.configure(bg="#d4d0c8")
        
        # --- Custom Title Bar (for consistent styling) ---
        self.overrideredirect(True) # Removes default OS window chrome
        self._offset_x = 0
        self._offset_y = 0

        title_bar = tk.Frame(self, bg="#0058d0", relief="raised", bd=0)
        title_bar.pack(side="top", fill="x")

        title_label = tk.Label(
            title_bar,
            text="SAMSOFT 1.0 A/B TESTING GEMINI 3.0 2HT [c] SAMSOFT INTERACTIVE 2025",
            bg="#0058d0",
            fg="white",
            font=("Roboto Mono", 8, "bold")
        )
        title_label.pack(side="left", padx=10)

        close_button = tk.Button(
            title_bar, text="X", command=self.destroy,
            bg="#e04040", fg="white", width=4, relief="raised", bd=1,
            activebackground="#c03030", activeforeground="white"
        )
        close_button.pack(side="right", padx=2, pady=2)

        # Add window drag functionality
        title_bar.bind("<Button-1>", self.start_move)
        title_bar.bind("<B1-Motion>", self.on_move)
        title_label.bind("<Button-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.on_move)

        # --- Menu Bar ---
        menu_bar = tk.Frame(self, bg="#d4d0c8", bd=1, relief="ridge")
        menu_bar.pack(side="top", fill="x", padx=2)
        
        file_menu = tk.Label(menu_bar, text="File", bg="#d4d0c8", padx=5)
        edit_menu = tk.Label(menu_bar, text="Edit", bg="#d4d0c8", padx=5)
        help_menu = tk.Label(menu_bar, text="Help", bg="#d4d0c8", padx=5)
        file_menu.pack(side="left")
        edit_menu.pack(side="left")
        help_menu.pack(side="left")

        # --- Toolbar ---
        toolbar = tk.Frame(self, bg="#e1e1e1", bd=1, relief="sunken")
        toolbar.pack(side="top", fill="x", padx=2, pady=(1, 0))
        
        active_font = font.Font(family="Roboto Mono", size=9, weight="bold")
        inactive_font = font.Font(family="Roboto Mono", size=9)

        item1 = tk.Label(
            toolbar, text="mele_ui.json", bg="#c0c0c0", font=active_font,
            relief="sunken", bd=1, padx=5, pady=2
        )
        item2 = tk.Label(
            toolbar, text="CHARACTER SELECT", bg="#e1e1e1", font=inactive_font, padx=5
        )
        item3 = tk.Label(
            toolbar, text="OPTIONS", bg="#e1e1e1", font=inactive_font, padx=5
        )
        item1.pack(side="left", padx=5, pady=3)
        item2.pack(side="left", padx=5, pady=3)
        item3.pack(side="left", padx=5, pady=3)

        # --- Main Canvas ---
        self.canvas = tk.Canvas(self, width=600, height=400, bg="#333333", highlightthickness=0)
        self.canvas.pack()

        self.draw_controller()

        # --- Status Bar ---
        status_bar = tk.Frame(self, bd=1, relief="sunken")
        status_bar.pack(side="bottom", fill="x", padx=2, pady=2)

        version_label = tk.Label(
            status_bar, text="VERSION: 1.2 (23HT BUILD)",
            bd=1, relief="sunken", anchor="w", padx=5
        )
        author_label = tk.Label(
            status_bar, text="AUTHOR: FLAMES CO LABS / SAMSOFT INTERACTIVE",
            bd=1, relief="sunken", anchor="w", padx=5
        )
        version_label.pack(side="left", fill="x", expand=True, padx=2, pady=2)
        author_label.pack(side="left", fill="x", expand=True, padx=2, pady=2)

        # --- Info Bubble (placed on top of the canvas) ---
        info_bubble = tk.Frame(self.canvas, bg="#f0f0f0", bd=1, relief="solid")
        info_bubble.place(x=380, y=10)
        tk.Label(info_bubble, text="HIGH-THROUGHPUT EXPERIMENTAL", font=("Roboto Mono", 7, "bold"), bg="#f0f0f0").pack(anchor="w")
        tk.Label(info_bubble, text="AB EVALUATION GEM", font=("Roboto Mono", 7), bg="#f0f0f0").pack(anchor="w")
        tk.Label(info_bubble, text="LICENSE: GPL-3.0 OR-LATER", font=("Roboto Mono", 7), bg="#f0f0f0").pack(anchor="w")

    def start_move(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def on_move(self, event):
        x = self.winfo_pointerx() - self._offset_x
        y = self.winfo_pointery() - self._offset_y
        self.geometry(f"+{x}+{y}")

    def draw_controller(self):
        # All coordinates are relative to the canvas
        # Center of the canvas
        cx, cy = 300, 220
        
        # Controller Body (approximated with a polygon)
        body_points = [
            cx-200, cy-10, cx-180, cy-50, cx-120, cy-80, cx+120, cy-80,
            cx+180, cy-50, cx+200, cy-10, cx+190, cy+60, cx+120, cy+90,
            cx-120, cy+90, cx-190, cy+60
        ]
        self.canvas.create_polygon(body_points, fill="#3a3d3a", outline="#222222", width=3)
        
        # Handles
        self.canvas.create_oval(cx-170, cy+20, cx-50, cy+150, fill="#3a3d3a", outline="#222222", width=2)
        self.canvas.create_oval(cx+50, cy+20, cx+170, cy+150, fill="#3a3d3a", outline="#222222", width=2)

        # --- Left Side ---
        # Left Joystick
        self.canvas.create_oval(cx-145, cy-40, cx-85, cy+20, fill="#2a2a2a", width=0)
        self.canvas.create_oval(cx-135, cy-30, cx-95, cy+10, fill="#444444", outline="#333333", width=2)
        
        # D-Pad
        self.canvas.create_oval(cx-90, cy+40, cx-20, cy+110, fill="#2a2a2a", width=0)
        self.canvas.create_rectangle(cx-80, cy+68, cx-30, cy+82, fill="#555555", outline="#4a4a4a", width=1)
        self.canvas.create_rectangle(cx-62, cy+50, cx-48, cy+100, fill="#555555", outline="#4a4a4a", width=1)
        
        # --- Right Side ---
        # Right Joystick
        self.canvas.create_oval(cx+85, cy+40, cx+145, cy+100, fill="#2a2a2a", width=0)
        self.canvas.create_oval(cx+95, cy+50, cx+135, cy+90, fill="#444444", outline="#333333", width=2)

        # ABXY Buttons
        btn_radius = 18
        btn_font = ("Arial", 16, "bold")
        
        # Y button
        self.canvas.create_oval(cx+102-btn_radius, cy-25-btn_radius, cx+102+btn_radius, cy-25+btn_radius, fill="#ffc20e", width=0)
        self.canvas.create_text(cx+102, cy-25, text="Y", fill="white", font=btn_font)
        # X button
        self.canvas.create_oval(cx+72-btn_radius, cy+5-btn_radius, cx+72+btn_radius, cy+5+btn_radius, fill="#0e84ff", width=0)
        self.canvas.create_text(cx+72, cy+5, text="X", fill="white", font=btn_font)
        # B button
        self.canvas.create_oval(cx+132-btn_radius, cy+5-btn_radius, cx+132+btn_radius, cy+5+btn_radius, fill="#ff3c3c", width=0)
        self.canvas.create_text(cx+132, cy+5, text="B", fill="white", font=btn_font)
        # A button
        self.canvas.create_oval(cx+102-btn_radius, cy+35-btn_radius, cx+102+btn_radius, cy+35+btn_radius, fill="#51c941", width=0)
        self.canvas.create_text(cx+102, cy+35, text="A", fill="white", font=btn_font)
        
        # --- Center Cluster ---
        # Back and Start buttons
        self.canvas.create_oval(cx-40, cy-15, cx-25, cy, fill="#444444", outline="#222222", width=1)
        self.canvas.create_oval(cx+25, cy-15, cx+40, cy, fill="#444444", outline="#222222", width=1)
        
        # Guide Button
        self.canvas.create_oval(cx-28, cy-45, cx+28, cy+11, fill="#cccccc", outline="#333333", width=3)
        # Guide Button X Logo (approximated with lines)
        self.canvas.create_line(cx-10, cy-28, cx+10, cy-8, fill="#51c941", width=4)
        self.canvas.create_line(cx-10, cy-8, cx+10, cy-28, fill="#51c941", width=4)


if __name__ == "__main__":
    app = App()
    app.mainloop()
