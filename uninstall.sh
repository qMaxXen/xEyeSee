#!/usr/bin/env bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "====================================="
echo "        xEyeSee uninstaller"
echo "====================================="
echo

INSTALL_DIR="$HOME/.local/bin"
LAUNCHER_LINK="$INSTALL_DIR/xeyesee"

if [ -L "$LAUNCHER_LINK" ]; then
    rm "$LAUNCHER_LINK"
    echo -e "${GREEN}Removed xeyesee from $INSTALL_DIR${NC}"
elif [ -e "$LAUNCHER_LINK" ]; then
    echo -e "${YELLOW}$LAUNCHER_LINK exists but is not a symlink. Removing anyway...${NC}"
    rm "$LAUNCHER_LINK"
    echo -e "${GREEN}Removed.${NC}"
else
    echo -e "${YELLOW}xeyesee was not found in $INSTALL_DIR. Nothing to remove.${NC}"
fi

echo
echo "Note: This only removes the terminal command."
echo "Neither the xEyeSee folder nor the config files were removed."
echo "To fully remove xEyeSee, delete the folder manually and remove the folder ~/.config/xEyeSee."
