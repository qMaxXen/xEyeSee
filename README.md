# xEyeSee

[![GitHub release](https://img.shields.io/github/v/release/qMaxXen/xEyeSee?logo=github)](https://github.com/qMaxXen/xEyeSee/releases)
[![GitHub downloads](https://img.shields.io/github/downloads/qMaxXen/xEyeSee/total?logo=github)](https://github.com/qMaxXen/xEyeSee/releases)

> [!IMPORTANT]
> This script works **only on Linux (X11).**

A lightweight Python program that displays an eye measuring projector when you eye zoom, without needing OBS Studio. 

<details>
  <summary>Demo Video [Click to expand]</summary>
  
  https://github.com/user-attachments/assets/c602660c-e822-4f47-b28d-1775656d1509

</details>

## Installation

1. Go to the [releases](https://github.com/qMaxXen/xEyeSee/releases/latest) section and download `xEyeSee-v1.2.1.tar.xz`.
2. Move the downloaded file to a convenient folder, then extract it using the terminal with the following command:

   ```bash
   tar -xf xEyeSee-v1.2.1.tar.xz
   ```
3. Install the required Python packages to run xEyeSee:

   ```bash
   cd xEyeSee-v1.2.1
   chmod +x install.sh
   ./install.sh
   ```
4. To run xEyeSee, type:
   ```bash
   xeyesee
   ```
   To configure xEyeSee, type:
   ```bash
   xeyesee --settings
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
- Run `xeyesee --settings` to change settings, such as eye zoom resolution, framerate, debug mode and source width.
- Zoom in further on the projector by setting the source width to `30`:
  - Run `xeyesee --settings`
  - Change `Source Width` to 30
  - Go to: https://qmaxxen.github.io/overlay-gen/
  - Generate a custom overlay with 'Overlay width' set to 30
  - Download the `overlay.png` file and place it in the main xEyeSee folder. (Make sure it is named `overlay.png`)
  - Restart xEyeSee to apply the new overlay
- The auto-updater notifies you when new versions are available and can download them automatically.

## License
xEyeSee is licensed under the MIT license. You can view the full license [here](https://raw.githubusercontent.com/qMaxXen/xEyeSee/refs/heads/main/LICENSE).

---

If you have any issues, feel free to ask for help by creating a thread in the [Linux MCSR Discord server](https://discord.gg/3tm4UpUQ8t).
