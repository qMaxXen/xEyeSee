import sys
import subprocess
import re
import os
import json
import shutil
import tempfile
import tarfile
import datetime
import numpy as np
import requests
from mss import mss
from PyQt5 import QtCore, QtGui, QtWidgets

DEBUG_MODE = False # Set to True to enable debug prints
GEOMETRY_POLL_MS = 200   # how often to check Minecraft geometry (ms). Default is 0.2s (200 ms). Higher = lower cpu usage.

# Program Version
APP_VERSION = "v1.1.1"

DEFAULT_ZOOM = (384, 16384, 768, -7652)
DEFAULT_SOURCE_WIDTH = 60

CONFIG_DIR = os.path.expanduser("~/.config/xEyeSee")
CONFIG_PATH = os.path.join(CONFIG_DIR, "info.json")

def log(*args, force=False):
    if DEBUG_MODE or force:
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        msg = " ".join(map(str, args))
        sys.stdout.write(f"{timestamp} {msg}\n")
        sys.stdout.flush()

def get_latest_github_release_version():
    url = "https://api.github.com/repos/qMaxXen/xEyeSee/releases/latest"
    try:
        resp = requests.get(url, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        return data.get("tag_name")
    except requests.exceptions.HTTPError as he:
        status = getattr(he.response, "status_code", None)
        if status == 403:
            print("[Version Check] rate limit hit, skipping update check.")
            return None
        print(f"[Version Check HTTPError] {he}")
        return None
    except Exception as e:
        print(f"[Version Check Error] {e}")
        return None

# ---------------------- AUTO UPDATER ----------------------
GITHUB_API = "https://api.github.com/repos/qMaxXen/xEyeSee/releases/latest"

def check_and_update(current_version):
    try:
        resp = requests.get(GITHUB_API, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        latest = data.get("tag_name")
        if not latest:
            print("[Updater] Could not read latest tag_name from GitHub response.")
            return

        if latest == current_version:
            print(f"[Updater] Already up to date ({current_version}).")
            return

        asset_name = f"xEyeSee-{latest}.tar.xz"
        folder_name = asset_name.replace(".tar.xz", "")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        folder_path = os.path.join(parent_dir, folder_name)

        if os.path.exists(folder_path):
            print(f"[Updater] Latest version ({latest}) already extracted at:")
            print(f"    {folder_path}")
            print("[Updater] Please navigate to that folder and run:")
            print("    ./install.sh")
            sys.exit(0)

        download_url = next(
            (a.get("browser_download_url") for a in data.get("assets", [])
             if a.get("name") == asset_name),
            None
        )
        if not download_url:
            print(f"[Updater] Asset {asset_name} not found in release {latest}.")
            return

        print(f"[Updater] Downloading {asset_name} …")
        tmpdir = tempfile.mkdtemp()
        archive_path = os.path.join(tmpdir, asset_name)
        with requests.get(download_url, stream=True, timeout=30) as dl:
            dl.raise_for_status()
            with open(archive_path, "wb") as f:
                for chunk in dl.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        print(f"[Updater] Extracting to {parent_dir} …")
        with tarfile.open(archive_path, "r:xz") as tar:
            tar.extractall(path=parent_dir)

        try:
            os.remove(archive_path)
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass

        body = data.get("body", "").strip()
        if body:
            print("\n[Updater] What's new:")
            print("-" * 40)
            print(body)
            print("-" * 40)

        print(f"\n[Updater] Update completed. New version extracted to:")
        print(f"    {folder_path}")
        print("[Updater] To finish setup, navigate to the new folder and run:")
        print("    chmod +x install.sh  # Make script executable")
        print("    ./install.sh         # Run installer")
        sys.exit(0)

    except requests.exceptions.HTTPError as he:
        status = getattr(he.response, "status_code", None)
        if status == 403:
            print("[Updater] Rate limit hit, skipping automatic update.")
            return
        print(f"[Updater] HTTP error when checking for updates: {he}")
    except Exception as e:
        print(f"[Updater] Update failed: {e}")

# ---------------------- AUTO UPDATER - END ----------------------


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
    source_width_in_file = data.get("source_width", None)

    if geom and all(k in geom for k in ("zoom_w", "zoom_h", "zoom_x", "zoom_y")) and isinstance(fps_in_file, int) and isinstance(source_width_in_file, int):
        w = int(geom.get("zoom_w", DEFAULT_ZOOM[0]))
        h = int(geom.get("zoom_h", DEFAULT_ZOOM[1]))
        x = int(geom.get("zoom_x", DEFAULT_ZOOM[2]))
        y = int(geom.get("zoom_y", DEFAULT_ZOOM[3]))
        fps = int(fps_in_file)
        src_w = int(source_width_in_file)
        debug = data.get("debug_mode", False)
        
        global DEBUG_MODE
        DEBUG_MODE = debug
        
        if DEBUG_MODE:
            log(f"\n=== Configuration Loaded from {CONFIG_PATH} ===")
            log(f"Eye zoom resolution: {w}x{h}+{x},{y}")
            log(f"Framerate: {fps} FPS")
            log(f"Source width: {src_w}")
            log(f"Debug mode: {'Enabled' if debug else 'Disabled'}")
            log(f"You can change these values using xEyeSee-settings.py\n")
        
        return (w, h, x, y, fps, src_w)

    if geom and all(k in geom for k in ("zoom_w", "zoom_h", "zoom_x", "zoom_y")):
        w = int(geom.get("zoom_w", DEFAULT_ZOOM[0]))
        h = int(geom.get("zoom_h", DEFAULT_ZOOM[1]))
        x = int(geom.get("zoom_x", DEFAULT_ZOOM[2]))
        y = int(geom.get("zoom_y", DEFAULT_ZOOM[3]))
        if DEBUG_MODE:
            print(f"Found existing eye zoom resolution in config: {w}x{h}+{x},{y}")
        


    else:
        print("Please enter your resolution in the format WxH+X,Y")
        print("For example: 384x16384+768,-7652")
        print("  W = width (pixels)\n  H = height (pixels)\n  X = X offset (pixels)\n  Y = Y offset (pixels)\n")
        
        while True:
            resp = input(f"Enter resolution (press Enter for default {DEFAULT_ZOOM[0]}x{DEFAULT_ZOOM[1]}+{DEFAULT_ZOOM[2]},{DEFAULT_ZOOM[3]}): ").strip()
            if not resp:
                w, h, x, y = DEFAULT_ZOOM
                break
            else:
                m = re.match(r"(\d+)x(\d+)\+(-?\d+),(-?\d+)", resp)
                if m:
                    w, h, x, y = map(int, m.groups())
                    break
                else:
                    print("Invalid format. Please try again.")
                    print("Format should be: WxH+X,Y (e.g., 384x16384+768,-7652)\n")

    if isinstance(fps_in_file, int) and fps_in_file > 0:
        fps = fps_in_file
        if DEBUG_MODE:
            print(f"Found existing framerate in config: {fps} FPS")
    else:
        while True:
            fps_resp = input("Enter the framerate at which the projector will be displayed (default 60): ").strip()
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

    if isinstance(source_width_in_file, int) and source_width_in_file in (30, 60):
        source_width = source_width_in_file
        if DEBUG_MODE:
            print(f"Found existing source width in config: {source_width}")
    else:
        print("Would you like to use source width 60 or 30?")
        print("  • 60 (default): Standard zoom level")
        print("  • 30: Allows for a more zoomed-in projector")
        while True:
            src_resp = input("Enter source width (30 or 60, default 60): ").strip()
            if src_resp == "":
                source_width = 60
                break
            if src_resp in ("30", "60"):
                source_width = int(src_resp)
                break
            else:
                print("Invalid input. Please enter either 30 or 60.")

    with open(CONFIG_PATH, "w") as f:
        json.dump({
            "eyezoom_resolution": {
                "zoom_w": w, "zoom_h": h,
                "zoom_x": x, "zoom_y": y
            },
            "framerate": int(fps),
            "source_width": int(source_width),
            "debug_mode": False
        }, f, indent=2)

    print(f"\nEye zoom resolution saved to {CONFIG_PATH}: {w}x{h}+{x},{y}")
    print(f"Framerate saved: {fps} FPS")
    print(f"Source width saved: {source_width}")
    print(f"You can change these values by running xEyeSee-settings.py\n")
    

    if source_width == 30:
        print("="*70)
        print("IMPORTANT: For a more zoomed-in projector with source width 30,\nyou must generate a custom overlay with an overlay width of 30,\notherwise your measurements won't be accurate:")
        print("  1. Go to: https://qmaxxen.github.io/overlay-gen/more-options/")
        print("  2. Generate a custom overlay with 'Overlay width' set to 30")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"  3. Download the overlay.png and place it in: {script_dir}")
        print("     Make sure the overlay file is named overlay.png")
        print("  4. Restart this script to use the new overlay")
        print("="*70)
        input("Press Enter to close...")
        sys.exit(0)
    return w, h, x, y, int(fps), int(source_width)    
        

TARGET_W, TARGET_H, TARGET_X, TARGET_Y, TARGET_FPS, TARGET_SOURCE_WIDTH = load_or_init_config()

if os.environ.get("XDG_SESSION_TYPE") == "wayland":
    print("ERROR: Wayland session detected. xEyeSee only works on X11.")
    input("Press Enter to close...")
    sys.exit(1)

print(f"xEyeSee version: {APP_VERSION}")
print("To change settings, run xEyeSee-settings.py")

latest = check_for_update(APP_VERSION)
if latest:
    print(f"\n=== New Release Available! ===")
    print(f"Version: {latest}")
    print("You should update to the latest version!")
    print("1) Continue with the current version")
    print("2) Automatically update to the latest version")
    choice = input("Enter choice [1/2]: ").strip() or "1"
    print()
    if choice == "2":
        check_and_update(APP_VERSION)
        input("Press Enter to close...")
    else:
        print("Skipping update. Continuing with current version", APP_VERSION, "\n")



missing = []
found = []
for cmd in ("wmctrl", "xwininfo"):
    if shutil.which(cmd) is None:
        missing.append(cmd)
    else:
        found.append(cmd)

if DEBUG_MODE and found:
    print(f"Required utilitie(s) found: {', '.join(found)}")

if missing:
    print(f"Error: Required command(s) not found: {', '.join(missing)}")
    print("Please install them:")
    print("  sudo apt install wmctrl x11-utils # [Debian/Ubuntu]")
    print("  sudo pacman -S wmctrl xorg-xwininfo # [Arch Linux]")
    print("  sudo dnf install xwininfo wmctrl # [Fedora]")
    input("Press Enter to close...")
    sys.exit(1)

PREVIEW_H = 600

OVERLAY_PATH = os.path.join(os.path.dirname(__file__), "overlay.png")

if not os.path.isfile(OVERLAY_PATH):
    print("Error: overlay.png is missing! Redownload the program from:")
    print("  https://github.com/qMaxXen/xEyeSee/releases")
    input("Press Enter to close...")
    sys.exit(1)
else:
    if DEBUG_MODE:
        print(f"Overlay found at: {OVERLAY_PATH}\n")

class MinecraftViewer(QtWidgets.QWidget):
    def __init__(self, x, y, w, h, fps=20):
        super().__init__()
        self.setWindowTitle("xEyeSee")
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

    def _recalc_and_position(self):
        SRC_W, SRC_H = TARGET_SOURCE_WIDTH, 580
        wx, wy = self.window_geom["left"], self.window_geom["top"]
        ww, wh = self.window_geom["width"], self.window_geom["height"]
        tx = wx + (ww - SRC_W) // 2
        ty = wy + (wh - SRC_H) // 2

        monitors = self.sct.monitors[1:]
        target_mon = monitors[0]
        window_center_x = wx + ww // 2
        window_center_y = wy + wh // 2

        for m in monitors:
            if (m["left"] <= window_center_x < m["left"] + m["width"] and
                m["top"] <= window_center_y < m["top"] + m["height"]):
                target_mon = m
                break

        tx = max(target_mon["left"], min(tx, target_mon["left"] + target_mon["width"] - SRC_W))
        ty = max(target_mon["top"], min(ty, target_mon["top"] + target_mon["height"] - SRC_H))

        self.capture_region = {"top": ty, "left": tx, "width": SRC_W, "height": SRC_H}

        space_on_left = wx - target_mon["left"]
        preview_w = max(1, min(space_on_left, target_mon["width"]))
        preview_h = min(PREVIEW_H, target_mon["height"])

        self.setFixedSize(preview_w, preview_h)
        self.label.setGeometry(0, 0, preview_w, preview_h)
        self.overlay_label.setGeometry(0, 0, preview_w, preview_h)

        desired_x = target_mon["left"]
        desired_y = wy + (wh - preview_h) // 2

        desired_y = max(target_mon["top"], min(desired_y, target_mon["top"] + target_mon["height"] - preview_h))

        self.move(desired_x, desired_y)

        if self.overlay_src:
            overlay_pix = self.overlay_src.scaled(
                preview_w, preview_h,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            self.overlay_label.setPixmap(overlay_pix)

        log(
            f"Monitor: {target_mon['width']}x{target_mon['height']}@({target_mon['left']},{target_mon['top']})"
        )
        log(
            f"Capture {SRC_W}×{SRC_H} @({tx},{ty}), preview {preview_w}×{preview_h} @({desired_x},{desired_y})"
        )

    def get_minecraft_window_title(self):
        try:
            out = subprocess.check_output(["wmctrl", "-l"], text=True)
            for line in out.splitlines():
                if '*' in line and "Minecraft" in line:
                    title = line.split(maxsplit=3)[-1]
                    if DEBUG_MODE:
                        log(f"Found Minecraft instance: {title}")
                    return title
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
            log("Waiting for Minecraft window...")
            return
        geo = self.get_geometry_from_xwininfo(title)
        if not geo:
            log(f"Failed to get geometry for: {title}")
            return

        x, y, w, h = geo
        old = (
            self.window_geom["left"],
            self.window_geom["top"],
            self.window_geom["width"],
            self.window_geom["height"]
        )
        if old != (x, y, w, h):
            log(f"Window moved/resized: {w}x{h}+{x},{y}")
            self.window_geom = {"top": y, "left": x, "width": w, "height": h}


        if (w, h, x, y) == (TARGET_W, TARGET_H, TARGET_X, TARGET_Y):
            if not self.active:
                self.active = True
                log(f"Eye zoom resolution matched ({w}x{h}+{x},{y}). Displaying eye measuring projector.")
            self._recalc_and_position()
            self.show()
            QtCore.QTimer.singleShot(50, self._recalc_and_position)

        else:
            if self.active:
                self.active = False
                log(f"Resolution is {w}x{h}+{x},{y} but expected {TARGET_W}x{TARGET_H}+{TARGET_X},{TARGET_Y}. Hiding projector.")
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
            log("Frame grab error:", e)

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
