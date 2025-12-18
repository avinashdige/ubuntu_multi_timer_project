#!/bin/bash
# Installation script for Multi-Timer Application

set -e

echo "==================================="
echo "Multi-Timer App Installation Script"
echo "==================================="
echo ""

# Check if running on Ubuntu/Debian
if ! command -v apt-get &> /dev/null; then
    echo "Error: This script requires apt-get (Ubuntu/Debian)"
    exit 1
fi

# Install system dependencies
echo "Step 1: Installing system dependencies..."
echo "This requires sudo access."
sudo apt-get update
sudo apt-get install -y \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    gir1.2-appindicator3-0.1 \
    gir1.2-notify-0.7 \
    libcanberra-gtk3-module \
    python3-dbus \
    python3-pip \
    python3.10-venv

echo ""
echo "Step 2: Creating virtual environment..."
echo "Using --system-site-packages to access system GTK libraries"
python3 -m venv --system-site-packages venv

echo ""
echo "Step 3: Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "==================================="
echo "Installation Complete!"
echo "==================================="
echo ""
echo "To run the application:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run: python3 timer_app/main.py"
echo ""
echo "Or create an alias in your ~/.bashrc:"
echo "  alias multi-timer='cd $(pwd) && source venv/bin/activate && python3 timer_app/main.py'"
echo ""
