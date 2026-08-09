import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import webbrowser

DEFAULT_ZOOM = (384, 16384, 768, -7652)
DEFAULT_SOURCE_WIDTH = 60
DEFAULT_FPS = 60
CONFIG_DIR = os.path.expanduser("~/.config/xEyeSee")
CONFIG_PATH = os.path.join(CONFIG_DIR, "info.json")

class SettingsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("xEyeSee Settings")
        self.root.geometry("600x730")
        self.root.resizable(False, False)
        self.load_settings()
        self.create_widgets()

    def load_settings(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)

        if os.path.isfile(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    data = json.load(f)

                geom = data.get("eyezoom_resolution", {})
                self.zoom_w = geom.get("zoom_w", DEFAULT_ZOOM[0])
                self.zoom_h = geom.get("zoom_h", DEFAULT_ZOOM[1])
                self.zoom_x = geom.get("zoom_x", DEFAULT_ZOOM[2])
                self.zoom_y = geom.get("zoom_y", DEFAULT_ZOOM[3])
                self.framerate = data.get("framerate", DEFAULT_FPS)
                self.source_width = data.get("source_width", DEFAULT_SOURCE_WIDTH)
                self.debug_mode = data.get("debug_mode", False)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.set_defaults()
        else:
            self.set_defaults()

    def set_defaults(self):
        self.zoom_w = DEFAULT_ZOOM[0]
        self.zoom_h = DEFAULT_ZOOM[1]
        self.zoom_x = DEFAULT_ZOOM[2]
        self.zoom_y = DEFAULT_ZOOM[3]
        self.framerate = DEFAULT_FPS
        self.source_width = DEFAULT_SOURCE_WIDTH
        self.debug_mode = False

    def create_widgets(self):
        title_label = tk.Label(
            self.root,
            text="xEyeSee Settings",
            font=("Arial", 18, "bold"),
            pady=15
        )
        title_label.pack()

        main_frame = ttk.Frame(self.root, padding=(20, 8))
        main_frame.pack(fill=tk.BOTH, expand=True)

        debug_frame = ttk.LabelFrame(main_frame, text="Debug Mode", padding="10")
        debug_frame.pack(fill=tk.X, pady=5)

        self.debug_var = tk.BooleanVar(value=self.debug_mode)
        debug_check = ttk.Checkbutton(
            debug_frame,
            text="Enable debug mode",
            variable=self.debug_var
        )
        debug_check.pack(anchor=tk.W)

        resolution_frame = ttk.LabelFrame(main_frame, text="Eye Zoom Resolution", padding="10")
        resolution_frame.pack(fill=tk.X, pady=5)

        width_row = ttk.Frame(resolution_frame)
        width_row.pack(fill=tk.X, pady=3)
        ttk.Label(width_row, text="Width (pixels):", width=20).pack(side=tk.LEFT)
        self.width_entry = ttk.Entry(width_row, width=15)
        self.width_entry.insert(0, str(self.zoom_w))
        self.width_entry.pack(side=tk.LEFT, padx=5)

        height_row = ttk.Frame(resolution_frame)
        height_row.pack(fill=tk.X, pady=3)
        ttk.Label(height_row, text="Height (pixels):", width=20).pack(side=tk.LEFT)
        self.height_entry = ttk.Entry(height_row, width=15)
        self.height_entry.insert(0, str(self.zoom_h))
        self.height_entry.pack(side=tk.LEFT, padx=5)

        x_row = ttk.Frame(resolution_frame)
        x_row.pack(fill=tk.X, pady=3)
        ttk.Label(x_row, text="X Offset (pixels):", width=20).pack(side=tk.LEFT)
        self.x_entry = ttk.Entry(x_row, width=15)
        self.x_entry.insert(0, str(self.zoom_x))
        self.x_entry.pack(side=tk.LEFT, padx=5)

        y_row = ttk.Frame(resolution_frame)
        y_row.pack(fill=tk.X, pady=3)
        ttk.Label(y_row, text="Y Offset (pixels):", width=20).pack(side=tk.LEFT)
        self.y_entry = ttk.Entry(y_row, width=15)
        self.y_entry.insert(0, str(self.zoom_y))
        self.y_entry.pack(side=tk.LEFT, padx=5)

        framerate_frame = ttk.LabelFrame(main_frame, text="Projector Framerate", padding="10")
        framerate_frame.pack(fill=tk.X, pady=5)

        fps_row = ttk.Frame(framerate_frame)
        fps_row.pack(fill=tk.X, pady=3)
        ttk.Label(fps_row, text="Framerate (FPS):", width=20).pack(side=tk.LEFT)
        self.fps_entry = ttk.Entry(fps_row, width=15)
        self.fps_entry.insert(0, str(self.framerate))
        self.fps_entry.pack(side=tk.LEFT, padx=5)

        source_frame = ttk.LabelFrame(main_frame, text="Source Width", padding="10")
        source_frame.pack(fill=tk.X, pady=5)

        self.source_var = tk.IntVar(value=self.source_width)

        source_60 = ttk.Radiobutton(
            source_frame,
            text="60 (Standard zoom level)",
            variable=self.source_var,
            value=60
        )
        source_60.pack(anchor=tk.W, pady=2)

        source_30 = ttk.Radiobutton(
            source_frame,
            text="30 (More zoomed-in projector)",
            variable=self.source_var,
            value=30
        )

        source_30.pack(anchor=tk.W, pady=2)

        info_frame = ttk.Frame(source_frame)
        info_frame.pack(anchor=tk.W, pady=(10, 5), fill=tk.X)

        script_dir = os.path.dirname(os.path.abspath(__file__))

        note_label = tk.Label(
            info_frame,
            text="IMPORTANT: If you are using source width 30, you must generate a custom overlay with an\noverlay width of 30, otherwise your measurements won't be accurate:",
            font=("Arial", 9, "bold"),
            anchor=tk.W,
            justify=tk.LEFT
        )
        note_label.pack(anchor=tk.W, pady=(0, 5))

        step1_frame = tk.Frame(info_frame)
        step1_frame.pack(anchor=tk.W)

        url = "https://qmaxxen.github.io/overlay-gen/"

        step1_label = tk.Label(
            step1_frame,
            text="1. Go to:",
            font=("Arial", 9),
            anchor=tk.W,
            justify=tk.LEFT
        )
        step1_label.pack(side=tk.LEFT)

        link_label = tk.Label(
            step1_frame,
            text=url,
            font=("Arial", 9, "underline"),
            fg="blue",
            cursor="hand2",
            anchor=tk.W,
            justify=tk.LEFT,
            bd=0
        )
        link_label.pack(side=tk.LEFT, padx=(2,0))

        link_label.bind("<Button-1>", lambda e: webbrowser.open(url))
        link_label.bind("<Enter>", lambda e: link_label.config(fg="#0000EE"))
        link_label.bind("<Leave>", lambda e: link_label.config(fg="blue"))


        step2_label = tk.Label(
            info_frame,
            text="2. Generate a custom overlay with 'Overlay width' set to 30",
            font=("Arial", 9),
            anchor=tk.W,
            justify=tk.LEFT
        )
        step2_label.pack(anchor=tk.W, pady=(5, 0))

        step3_frame = tk.Frame(info_frame)
        step3_frame.pack(anchor=tk.W, fill=tk.X)

        step3_label = tk.Label(
            step3_frame,
            text="3. Download the overlay.png and place it in:",
            font=("Arial", 9),
            anchor=tk.W,
            justify=tk.LEFT
        )
        step3_label.pack(side=tk.LEFT)

        path_entry = tk.Entry(
            step3_frame,
            font=("Arial", 9),
            bd=0,
            highlightthickness=0,
            relief="flat",
            readonlybackground=self.root.cget('bg'),
            cursor="arrow",
            width=45
        )
        path_entry.insert(0, script_dir)
        path_entry.config(state="readonly", justify="left")
        path_entry.pack(side=tk.LEFT, padx=(2,0), fill=tk.X, expand=True)

        step3b_label = tk.Label(
            info_frame,
            text="    Make sure the overlay file is named overlay.png",
            font=("Arial", 9, "bold"),
            anchor=tk.W,
            justify=tk.LEFT
        )
        step3b_label.pack(anchor=tk.W)

        step4_label = tk.Label(
            info_frame,
            text="4. Restart xEyeSee to update the overlay",
            font=("Arial", 9),
            anchor=tk.W,
            justify=tk.LEFT
        )
        step4_label.pack(anchor=tk.W, pady=(5, 0))

        button_frame = ttk.Frame(main_frame, padding=(6, 4))
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(6, 4))

        save_btn = ttk.Button(
            button_frame,
            text="Save Settings",
            command=self.save_settings,
            width=15
        )
        save_btn.pack(side=tk.LEFT, padx=(4,2), pady=2)

        reset_btn = ttk.Button(
            button_frame,
            text="Reset to Default",
            command=self.reset_to_default,
            width=15
        )
        reset_btn.pack(side=tk.LEFT, padx=(2,4), pady=2)

        exit_btn = ttk.Button(
            button_frame,
            text="Exit",
            command=self.root.quit,
            width=15
        )
        exit_btn.pack(side=tk.RIGHT, padx=4, pady=2)


    def validate_inputs(self):
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            fps = int(self.fps_entry.get())

            if width <= 0 or height <= 0:
                messagebox.showerror("Invalid Input", "Width and Height must be positive numbers.")
                return None

            if fps <= 0:
                messagebox.showerror("Invalid Input", "Framerate must be a positive number.")
                return None

            return {
                "width": width,
                "height": height,
                "x": x,
                "y": y,
                "fps": fps
            }
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for all fields.")
            return None

    def save_settings(self):
        validated = self.validate_inputs()
        if validated is None:
            return

        config_data = {
            "eyezoom_resolution": {
                "zoom_w": validated["width"],
                "zoom_h": validated["height"],
                "zoom_x": validated["x"],
                "zoom_y": validated["y"]
            },
            "framerate": validated["fps"],
            "source_width": self.source_var.get(),
            "debug_mode": self.debug_var.get()
        }

        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_PATH, "w") as f:
                json.dump(config_data, f, indent=2)

            messagebox.showinfo(
                "Settings Saved",
                f"Your settings have been saved successfully!"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def reset_to_default(self):
        response = messagebox.askyesno(
            "Reset to Default",
            "Are you sure you want to reset all settings to their default values?"
        )

        if response:
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(DEFAULT_ZOOM[0]))

            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(DEFAULT_ZOOM[1]))

            self.x_entry.delete(0, tk.END)
            self.x_entry.insert(0, str(DEFAULT_ZOOM[2]))

            self.y_entry.delete(0, tk.END)
            self.y_entry.insert(0, str(DEFAULT_ZOOM[3]))

            self.fps_entry.delete(0, tk.END)
            self.fps_entry.insert(0, str(DEFAULT_FPS))

            self.source_var.set(DEFAULT_SOURCE_WIDTH)
            self.debug_var.set(False)
def main():
    root = tk.Tk()
    app = SettingsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
