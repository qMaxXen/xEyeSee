# xEyeSee

[![GitHub release](https://img.shields.io/github/v/release/qMaxXen/xEyeSee?logo=github)](https://github.com/qMaxXen/xEyeSee/releases)
[![GitHub downloads](https://img.shields.io/github/downloads/qMaxXen/xEyeSee/total?logo=github)](https://github.com/qMaxXen/xEyeSee/releases)

> [!IMPORTANT]
> This script works **only on Linux (X11).**

Lightweight Python script that displays a standalone eye measuring projector, made as a Linux alternative to the Windows-only [Jingle-EyeSee](https://github.com/DuncanRuns/Jingle-EyeSee-Plugin).

<details>
  <summary>Demo Video [Click to expand]</summary>

  https://github.com/user-attachments/assets/9a1762d9-7bbf-4db4-beb4-8959d91bda0b

</details>


## Installation

1. Go to the [Releases](https://github.com/qMaxXen/xEyeSee/releases/tag/v1.0.2) section and download `xEyeSee-v1.0.2.tar.xz`.
2. Move the downloaded file to a convenient folder, then extract it:
   ```bash
   tar -xf xEyeSee-v1.0.2.tar.xz
   ```
3. Install the required Python packages:
   ```bash
   cd xEyeSee-v1.0.2
   pip3 install -r requirements.txt
   ```
4. Install the required utilities:
  - Debian/Ubuntu: `sudo apt install wmctrl x11-utils`
  - Arch Linux: `sudo pacman -S wmctrl xorg-xwininfo`
  - Fedora: `sudo dnf install xwininfo wmctrl`
5. Run the script:
   ```bash
   python3 xEyeSee.py
   ```

## Features

- Asks for your **eye zoom resolution** (format: `WxH+X,Y`) on first launch. 
  - W = width (pixels)  
  - H = height (pixels)
  - X = X offset (pixels)
  - Y = Y offset (pixels)
  - Your resolution gets saved to `~/.config/xEyeSee/info.json`.
- Automatically displays the eye measuring projector when Minecraft is resized to eye zoom.
- Customizable framerate at which the frame is displayed.
- **Customizable overlay:** simply replace the included `overlay.png` with your own image overlay. (must be named `overlay.png`)

### Miscellaneous
- Built-in update checker: notifies you when a new version is available.
- `DEBUG_MODE` option: toggle to show or hide console output.


---

If you need help or have any questions, feel free to contact me on Discord: **qMaxXen**.
