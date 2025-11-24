# xEyeSee

[![GitHub release](https://img.shields.io/github/v/release/qMaxXen/xEyeSee?logo=github)](https://github.com/qMaxXen/xEyeSee/releases)
[![GitHub downloads](https://img.shields.io/github/downloads/qMaxXen/xEyeSee/total?logo=github)](https://github.com/qMaxXen/xEyeSee/releases)

> [!IMPORTANT]
> This script works **only on Linux (X11).**

A lightweight Python script that displays an eye measuring projector when you eye zoom, without needing OBS Studio. 

<details>
  <summary>Demo Video [Click to expand]</summary>
  
  https://github.com/user-attachments/assets/c602660c-e822-4f47-b28d-1775656d1509

</details>

## Installation

1. Go to the [Releases](https://github.com/qMaxXen/xEyeSee/releases/tag/v1.1.1) section and download `xEyeSee-v1.1.1.tar.xz`.
2. Move the downloaded file to a convenient folder, then extract it:
   ```bash
   tar -xf xEyeSee-v1.1.1.tar.xz
   ```
3. Install the required Python packages:
   ```bash
   cd xEyeSee-v1.1.1
   pip3 install -r requirements.txt
   ```
> [!TIP]
> Getting the `PEP 668 (externally-managed-environment)` error after running `pip3 install -r requirements.txt`? Create a Python virtual environment:
> ```bash
> # Make sure you are in the extracted folder
> python3 -m venv venv
> source venv/bin/activate
> pip install -r requirements.txt
> ```
> To run the script from the terminal without needing to enter the venv, use the Python binary inside the venv:
> ```bash
> /full/path/to/venv/bin/python <script>.py
> ```

4. Install the required utilities:
  - Debian/Ubuntu: `sudo apt install wmctrl x11-utils`
  - Arch Linux: `sudo pacman -S wmctrl xorg-xwininfo`
  - Fedora: `sudo dnf install xwininfo wmctrl`
5. Run the script:
   ```bash
   python3 xEyeSee.py
   ```

## Features

- On first launch, you will be asked to enter your eye zoom resolution in the format `WxH+X,Y`: 
  - W = width (pixels)  
  - H = height (pixels)
  - X = X offset (pixels)
  - Y = Y offset (pixels)
- The eye measuring projector displays automatically when eye zoom is enabled.
- You can customize the framerate of the eye measuring projector.
- You can use a custom overlay by replacing the included `overlay.png` with your own overlay (must be named `overlay.png`).
- You can use `xEyeSee-settings.py` to change settings, such as eye zoom resolution, framerate, debug mode and source width.
- Zoom in further on the projector by setting the source width to `30`:
  - Run `xEyeSee-settings.py` inside the main `xEyeSee` folder
  - Change `Source Width` to 30
  - Go to: https://qmaxxen.github.io/overlay-gen/more-options/
  - Generate a custom overlay with 'Overlay width' set to 30
  - Download the `overlay.png` file and place it in the main xEyeSee folder. Make sure it is named `overlay.png`
  - Restart xEyeSee to apply the new overlay
- The auto-updater notifies you when new versions are available and can download them automatically.

<img width="400" height="500" alt="image" src="https://github.com/user-attachments/assets/f88cd056-9dd6-4320-ac3c-ceb746c83903" />

## License
xEyeSee is licensed under the MIT license. You can view the full license [here](https://raw.githubusercontent.com/qMaxXen/xEyeSee/refs/heads/main/LICENSE).

---

If you need help or have any questions, feel free to contact me on Discord: **qMaxXen**.
