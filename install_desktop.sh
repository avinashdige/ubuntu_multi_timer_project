#!/bin/bash
# Desktop Integration Installation Script for Multi-Timer App

set -e

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_FILE="multi-timer.desktop"
AUTOSTART_FILE="multi-timer-autostart.desktop"

# Desktop file installation paths
APPLICATIONS_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"

echo "=========================================="
echo "Multi-Timer Desktop Integration Installer"
echo "=========================================="
echo ""
echo "Project directory: $PROJECT_DIR"
echo ""

# Create directories if they don't exist
mkdir -p "$APPLICATIONS_DIR"
mkdir -p "$AUTOSTART_DIR"

# Function to create desktop file with correct paths
create_desktop_file() {
    local file_path="$1"
    local file_name="$2"

    cat > "$file_path" << EOF
[Desktop Entry]
Version=1.2
Type=Application
Name=Multi Timer
GenericName=Timer Application
Comment=Manage multiple named timers with desktop notifications
Icon=alarm-clock
Exec=$PROJECT_DIR/run.sh
Path=$PROJECT_DIR
Terminal=false
Categories=Utility;Clock;
Keywords=timer;alarm;countdown;notification;
StartupNotify=true
EOF

    echo "Created: $file_path"
}

# Function to create autostart desktop file
create_autostart_file() {
    local file_path="$1"

    cat > "$file_path" << EOF
[Desktop Entry]
Type=Application
Name=Multi Timer
Comment=Manage multiple named timers with desktop notifications
Icon=alarm-clock
Exec=$PROJECT_DIR/run.sh
Path=$PROJECT_DIR
Terminal=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
Hidden=false
EOF

    echo "Created: $file_path"
}

# Install application launcher
echo "Step 1: Installing application launcher..."
APP_DESKTOP_PATH="$APPLICATIONS_DIR/$DESKTOP_FILE"
create_desktop_file "$APP_DESKTOP_PATH" "$DESKTOP_FILE"
chmod +x "$APP_DESKTOP_PATH"
echo "✓ Application launcher installed"
echo ""

# Ask about autostart
echo "Step 2: Auto-start configuration"
read -p "Do you want Multi-Timer to start automatically when you log in? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    AUTOSTART_PATH="$AUTOSTART_DIR/$AUTOSTART_FILE"
    create_autostart_file "$AUTOSTART_PATH"
    chmod +x "$AUTOSTART_PATH"
    echo "✓ Auto-start enabled"
    echo "  The app will launch automatically when you log in"
else
    # Remove autostart file if it exists
    if [ -f "$AUTOSTART_DIR/$AUTOSTART_FILE" ]; then
        rm "$AUTOSTART_DIR/$AUTOSTART_FILE"
        echo "✓ Auto-start disabled"
    else
        echo "✓ Auto-start not configured"
    fi
fi
echo ""

# Update desktop database
echo "Step 3: Updating desktop database..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true
    echo "✓ Desktop database updated"
else
    echo "⚠ update-desktop-database not found (this is optional)"
fi
echo ""

echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Multi-Timer is now available as a desktop application."
echo ""
echo "How to use:"
echo "  1. Press Super key (Windows key) and search for 'Multi Timer'"
echo "  2. Click the icon to launch the application"
echo "  3. The app will appear in your system tray (top bar)"
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Auto-start: ENABLED"
    echo "  - The app will launch automatically on next login"
    echo "  - To disable: Run this script again or remove:"
    echo "    $AUTOSTART_DIR/$AUTOSTART_FILE"
else
    echo "Auto-start: DISABLED"
    echo "  - To enable: Run this script again and choose 'y'"
fi
echo ""
echo "To uninstall desktop integration:"
echo "  ./uninstall_desktop.sh"
echo ""
