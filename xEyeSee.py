import sys
import subprocess
import re
import os
import json
import shutil
import numpy as np
import requests
from mss import mss
from PyQt5 import QtCore, QtGui, QtWidgets

DEBUG_MODE = False # Set to True to enable debug prints
GEOMETRY_POLL_MS = 200   # how often to check Minecraft geometry (ms). Default is 0.2s (200 ms). Higher = lower cpu usage.

# Program Version
APP_VERSION = "v1.0.2"

DEFAULT_ZOOM = (320, 16384, 800, -7652)

CONFIG_DIR = os.path.expanduser("~/.config/xEyeSee")
CONFIG_PATH = os.path.join(CONFIG_DIR, "info.json")
def get_latest_github_release_version():
    url = "https://api.github.com/repos/qMaxXen/xEyeSee/releases/latest"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("tag_name")
    except Exception as e:
        print(f"[Version Check Error] {e}")
        return None

def check_for_update(current_version):
    latest_version = get_latest_github_release_version()
    if latest_version and latest_version != current_version:
        return latest_version
    return None

def load_or_init_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    data = {}

    if os.path.isfile(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
        except Exception:
            data = {}

    geom = data.get("eyezoom_resolution")
    fps_in_file = data.get("framerate", None)

    if geom and all(k in geom for k in ("zoom_w", "zoom_h", "zoom_x", "zoom_y")) and isinstance(fps_in_file, int):
        return (
            int(geom.get("zoom_w", DEFAULT_ZOOM[0])),
            int(geom.get("zoom_h", DEFAULT_ZOOM[1])),
            int(geom.get("zoom_x", DEFAULT_ZOOM[2])),
            int(geom.get("zoom_y", DEFAULT_ZOOM[3])),
            int(fps_in_file),
        )

    if geom and all(k in geom for k in ("zoom_w", "zoom_h", "zoom_x", "zoom_y")):
        w = int(geom.get("zoom_w", DEFAULT_ZOOM[0]))
        h = int(geom.get("zoom_h", DEFAULT_ZOOM[1]))
        x = int(geom.get("zoom_x", DEFAULT_ZOOM[2]))
        y = int(geom.get("zoom_y", DEFAULT_ZOOM[3]))
        if DEBUG_MODE:
            print(f"Found existing eyezoom resolution in config: {w}x{h}+{x},{y}")
        
    else:
        print("Please enter your eyezoom resolution in the format WxH+X,Y")
        print("For example: 320x16384+800,-7652")
        print("  W = width (pixels)\n  H = height (pixels)\n  X = X offset (pixels)\n  Y = Y offset (pixels)\n")
        resp = input(f"Enter resolution (press Enter for default {DEFAULT_ZOOM[0]}x{DEFAULT_ZOOM[1]}+{DEFAULT_ZOOM[2]},{DEFAULT_ZOOM[3]}): ").strip()
        if not resp:
            w, h, x, y = DEFAULT_ZOOM
        else:
            m = re.match(r"(\d+)x(\d+)\+(-?\d+),(-?\d+)", resp)
            if m:
                w, h, x, y = map(int, m.groups())
            else:
                print("Invalid format, using default.")
                w, h, x, y = DEFAULT_ZOOM

    if isinstance(fps_in_file, int) and fps_in_file > 0:
        fps = fps_in_file
        if DEBUG_MODE:
            print(f"Found existing framerate in config: {fps} FPS")
    else:
        while True:
            fps_resp = input("Enter the framerate at which the frame will be displayed (default 60): ").strip()
            if fps_resp == "":
                fps = 60
                break
            try:
                fps = int(fps_resp)
                if fps <= 0:
                    print("Please enter a positive number for framerate.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a number (e.g. 30, 60).")

    with open(CONFIG_PATH, "w") as f:
        json.dump({
            "eyezoom_resolution": {
                "zoom_w": w, "zoom_h": h,
                "zoom_x": x, "zoom_y": y
            },
            "framerate": int(fps)
        }, f, indent=2)

    print(f"Eyezoom resolution saved to {CONFIG_PATH}: {w}x{h}+{x},{y}")
    print(f"Framerate saved: {fps} FPS")
    print(f"You can change both these values in {CONFIG_PATH}.")
    return w, h, x, y, int(fps)


TARGET_W, TARGET_H, TARGET_X, TARGET_Y, TARGET_FPS = load_or_init_config()

if os.environ.get("XDG_SESSION_TYPE") == "wayland":
    print("Warning: Wayland session detected. xEyeSee only works on X11 for now.\n")

print(f"xEyeSee version: {APP_VERSION}")

latest = check_for_update(APP_VERSION)
if latest:
    print(f"\n=== New Release Available! ===")
    print(f"Version: {latest}")
    print("You should update to the latest version!")
    print("https://github.com/qMaxXen/xEyeSee/releases\n")
    input("Press Enter to continue...")
    print("==============================")

missing = []
for cmd in ("wmctrl", "xwininfo"):
    if shutil.which(cmd) is None:
        missing.append(cmd)
if missing:
    print(f"Error: Required command(s) not found: {', '.join(missing)}")
    print("Please install them, e.g.:")
    print("  sudo apt install wmctrl x11-utils # [Debian]")
    print("  sudo pacman -S wmctrl xorg-xwininfo # [Arch Linux]")
    print("  sudo dnf install xwininfo wmctrl # [Fedora]")
    sys.exit(1)


PREVIEW_H = 600

OVERLAY_PATH = os.path.join(os.path.dirname(__file__), "overlay.png")

if not os.path.isfile(OVERLAY_PATH):
    print("Error: overlay.png is missing! Redownload the program from:")
    print("  https://github.com/qMaxXen/xEyeSee/releases")
    sys.exit(1)

class MinecraftViewer(QtWidgets.QWidget):
    def __init__(self, x, y, w, h, fps=20):
        super().__init__()
        self.setWindowTitle("Minecraft Live Preview")
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool |
            QtCore.Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)

        self.window_geom = {"top": y, "left": x, "width": w, "height": h}

        screen = mss().monitors[1]
        self.screen_h, self.screen_w = screen["height"], screen["width"]

        self.label = QtWidgets.QLabel(self)
        self.label.setScaledContents(False)

        self.overlay_label = QtWidgets.QLabel(self)
        self.overlay_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.overlay_label.setScaledContents(False)
        self.overlay_label.setAlignment(QtCore.Qt.AlignCenter)

        self.overlay_src = (
            QtGui.QPixmap(OVERLAY_PATH) if os.path.exists(OVERLAY_PATH) else None
        )

        self.sct = mss()

        self.active = False
        self.hide()

        self.timer = QtCore.QTimer(self, timeout=self.update_frame)
        self.timer.start(int(1000 / fps))
        self.window_poll_timer = QtCore.QTimer(self, timeout=self.check_minecraft_geometry)
        self.window_poll_timer.start(GEOMETRY_POLL_MS)

    def debug(self, *args):
        if DEBUG_MODE:
            print(*args)

    def _recalc_and_position(self):
        SRC_W, SRC_H = 60, 580
        wx, wy = self.window_geom["left"], self.window_geom["top"]
        ww, wh = self.window_geom["width"], self.window_geom["height"]
        tx = wx + (ww - SRC_W) // 2
        ty = wy + (wh - SRC_H) // 2
        self.capture_region = {"top": ty, "left": tx, "width": SRC_W, "height": SRC_H}

        preview_w = max(1, min(wx, self.screen_w))
        preview_h = min(PREVIEW_H, self.screen_h)

        self.setFixedSize(preview_w, preview_h)
        self.label.setGeometry(0, 0, preview_w, preview_h)
        self.overlay_label.setGeometry(0, 0, preview_w, preview_h)

        desired_x, desired_y = 0, wy + (wh - preview_h) // 2
        desired_y = max(0, min(desired_y, self.screen_h - preview_h))
        self.move(desired_x, desired_y)

        if self.overlay_src:
            overlay_pix = self.overlay_src.scaled(
                preview_w, preview_h,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            self.overlay_label.setPixmap(overlay_pix)

        self.debug(
            f"Capture 60×580 @({tx},{ty}), preview {preview_w}×{preview_h} @({desired_x},{desired_y})"
        )

    def get_minecraft_window_title(self):
        try:
            out = subprocess.check_output(["wmctrl", "-l"], text=True)
            for line in out.splitlines():
                if '*' in line and "Minecraft" in line:
                    return line.split(maxsplit=3)[-1]
        except subprocess.CalledProcessError:
            pass
        return None

    def get_geometry_from_xwininfo(self, window_name):
        try:
            out = subprocess.check_output(
                ["xwininfo", "-name", window_name], text=True
            )
            m = re.search(r"-geometry\s+(\d+)x(\d+)\+([-\d]+)\+([-\d]+)", out)
            if m:
                w, h, x, y = map(int, m.groups())
                return x, y, w, h
        except subprocess.CalledProcessError:
            pass
        return None

    def check_minecraft_geometry(self):
        title = self.get_minecraft_window_title()
        if not title:
            return
        geo = self.get_geometry_from_xwininfo(title)
        if not geo:
            return

        x, y, w, h = geo
        old = (
            self.window_geom["left"],
            self.window_geom["top"],
            self.window_geom["width"],
            self.window_geom["height"]
        )
        if old != (x, y, w, h):
            self.window_geom = {"top": y, "left": x, "width": w, "height": h}

        if (w, h, x, y) == (TARGET_W, TARGET_H, TARGET_X, TARGET_Y):
            if not self.active:
                self.active = True
                self.debug("Resolution matched. Showing live preview.")
            self._recalc_and_position()
            self.show()
            QtCore.QTimer.singleShot(50, self._recalc_and_position)
        
        else:
            if self.active:
                self.active = False
                self.debug("Resolution no longer matches. Hiding preview.")
                self.hide()

    def update_frame(self):
        if not self.active:
            return
        try:
            img = self.sct.grab(self.capture_region)
            arr = np.array(img)[:, :, :3]
            rgb = arr[..., ::-1]

            h, w, ch = rgb.shape
            qimg = QtGui.QImage(rgb.tobytes(), w, h, ch*w,
                                QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap.fromImage(qimg)

            preview_w, preview_h = self.width(), self.height()
            scaled = pix.scaled(
                preview_w, preview_h,
                QtCore.Qt.IgnoreAspectRatio,
                QtCore.Qt.FastTransformation
            )
            self.label.setPixmap(scaled)
        except Exception as e:
            if DEBUG_MODE:
                print("Frame grab error:", e)

    def closeEvent(self, event):
        self.timer.stop()
        self.window_poll_timer.stop()
        self.sct.close()
        event.accept()

def main():
    app = QtWidgets.QApplication(sys.argv)
    viewer = MinecraftViewer(0, 0, 100, 100, fps=TARGET_FPS)
    viewer.hide()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
