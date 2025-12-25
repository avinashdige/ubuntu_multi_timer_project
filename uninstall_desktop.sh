#!/bin/bash
# Desktop Integration Uninstallation Script for Multi-Timer App

DESKTOP_FILE="multi-timer.desktop"
AUTOSTART_FILE="multi-timer-autostart.desktop"

APPLICATIONS_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"

APP_DESKTOP_PATH="$APPLICATIONS_DIR/$DESKTOP_FILE"
AUTOSTART_PATH="$AUTOSTART_DIR/$AUTOSTART_FILE"

echo "=========================================="
echo "Multi-Timer Desktop Uninstaller"
echo "=========================================="
echo ""

removed=0

# Remove application launcher
if [ -f "$APP_DESKTOP_PATH" ]; then
    rm "$APP_DESKTOP_PATH"
    echo "✓ Removed application launcher"
    removed=1
else
    echo "⚠ Application launcher not found"
fi

# Remove autostart file
if [ -f "$AUTOSTART_PATH" ]; then
    rm "$AUTOSTART_PATH"
    echo "✓ Removed auto-start configuration"
    removed=1
else
    echo "⚠ Auto-start configuration not found"
fi

# Update desktop database
if [ $removed -eq 1 ]; then
    echo ""
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true
        echo "✓ Desktop database updated"
    fi
    echo ""
    echo "=========================================="
    echo "Uninstallation Complete!"
    echo "=========================================="
    echo ""
    echo "Desktop integration has been removed."
    echo "Multi-Timer will no longer appear in the application menu"
    echo "or auto-start at login."
    echo ""
    echo "Note: The application files are still in:"
    echo "  $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo ""
    echo "You can still run the app manually with: ./run.sh"
    echo ""
else
    echo ""
    echo "No desktop integration found to remove."
    echo ""
fi
