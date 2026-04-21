#!/usr/bin/env bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m'
CYAN='\033[0;36m'

echo "==================================="
echo "        xEyeSee installer"
echo "==================================="
echo

if command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
elif command -v python &>/dev/null; then
    PYTHON_BIN="python"
else
    echo -e "${RED}ERROR: Python is not installed.${NC}"
    echo "Install it via your distro package manager:"
    echo "  Debian/Ubuntu: sudo apt install python3"
    echo "  Arch Linux:    sudo pacman -S python"
    echo "  Fedora:        sudo dnf install python3"
    exit 1
fi

MISSING_UTILS=()
if ! command -v wmctrl &>/dev/null; then MISSING_UTILS+=("wmctrl"); fi
if ! command -v xwininfo &>/dev/null; then MISSING_UTILS+=("x11-utils or xorg-xwininfo"); fi

if [ ${#MISSING_UTILS[@]} -ne 0 ]; then
    echo -e "${RED}ERROR: Missing system utilities: ${MISSING_UTILS[*]}${NC}"
    echo "Please install them to make sure xEyeSee works properly:"
    echo "  Debian/Ubuntu: sudo apt install wmctrl x11-utils"
    echo "  Arch Linux:    sudo pacman -S wmctrl xorg-xwininfo"
    echo "  Fedora:        sudo dnf install xwininfo wmctrl"
    echo
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    "$PYTHON_BIN" -m venv venv
else
    echo "Virtual environment already exists."
fi

FULL_PATH="$(pwd)/venv/bin/python"

"$FULL_PATH" - <<'EOF'
import sys
try:
    import pip
except ImportError:
    print("ERROR: pip is not installed in this virtual environment.")
    print("Installation of xEyeSee dependencies will fail.")
    print("You can try to fix this by running:")
    print(f"  {sys.executable} -m ensurepip")
    print("Or manually via:")
    print("  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py")
    print(f"  {sys.executable} get-pip.py")
    sys.exit(1)
EOF

"$FULL_PATH" - <<'EOF'
import sys
RED='\033[1;31m'
NC='\033[0m'
try:
    import tkinter
except ImportError:
    print(f"{RED}ERROR: tkinter is not installed.{NC}")
    print("This is required for the xEyeSee Settings GUI.")
    print("Install it via your distro package manager:")
    print("  Debian/Ubuntu: sudo apt install python3-tk")
    print("  Arch Linux:    sudo pacman -S tk")
    print("  Fedora:        sudo dnf install python3-tkinter")
    sys.exit(1)
EOF

echo "Installing required Python packages..."
"$FULL_PATH" -m pip install --upgrade pip
"$FULL_PATH" -m pip install -r requirements.txt

echo
echo -e "${GREEN}Installation complete!${NC}"
echo

INSTALL_DIR="$HOME/.local/bin"
LAUNCHER_TARGET="$(pwd)/xeyesee"
LAUNCHER_LINK="$INSTALL_DIR/xeyesee"

chmod +x "$LAUNCHER_TARGET"
mkdir -p "$INSTALL_DIR"

if [ -L "$LAUNCHER_LINK" ] || [ -e "$LAUNCHER_LINK" ]; then
    echo "Updating existing xeyesee entry in $INSTALL_DIR..."
    ln -sf "$LAUNCHER_TARGET" "$LAUNCHER_LINK"
else
    ln -sf "$LAUNCHER_TARGET" "$LAUNCHER_LINK"
    echo -e "${GREEN}xEyeSee terminal command added to $INSTALL_DIR${NC}"
fi

case ":$PATH:" in
    *":$INSTALL_DIR:"*)
        ;;
    *)
        echo
        echo -e "${YELLOW}$INSTALL_DIR is not in your PATH.${NC}"
        echo "Add this line to your shell config (~/.bashrc, ~/.zshrc, etc.):"
        echo
        echo -e "  ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
        echo
        echo "Then restart your terminal."
        ;;
esac
echo

echo "To run xEyeSee:"
echo -e "  ${CYAN}xeyesee${NC}"
echo
echo "To configure xEyeSee:"
echo -e "  ${CYAN}xeyesee --settings${NC}"
echo
echo "To remove xEyeSee from your terminal, run:"
echo -e "  ${CYAN}./uninstall.sh${NC}"
