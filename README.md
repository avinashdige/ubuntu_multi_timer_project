# Multi-Timer Application

A system tray application for Ubuntu that allows you to manage multiple named timers simultaneously with desktop notifications and sound alerts.

## Features

- **System Tray Integration**: Runs in Ubuntu's top bar with a clickable icon
- **Multiple Timers**: Create and manage unlimited concurrent timers
- **Real-Time Countdown**: View all active timers with live countdown display
- **Desktop Notifications**: Get notified with sound when timers complete
- **Simple Interface**: Quick and easy timer creation with hours, minutes, and seconds
- **One-Click Management**: Delete timers instantly with a single click

## Prerequisites

### System Dependencies

Install required Ubuntu packages:

```bash
sudo apt-get update
sudo apt-get install -y \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    gir1.2-appindicator3-0.1 \
    gir1.2-notify-0.7 \
    libcanberra-gtk3-module \
    python3-dbus \
    python3-pip
```

### Python Requirements

Python 3.7 or higher is required.

## Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (with system site packages to access GTK):

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

3. **Install Python dependencies**:

```bash
pip install -r requirements.txt
```

**Note**: We use `--system-site-packages` to access system-installed PyGObject and GTK libraries, which are difficult to install via pip.

## Running the Application

### Method 1: Direct Execution

```bash
python3 timer_app/main.py
```

### Method 2: If Installed as Package

```bash
multi-timer
```

The application will start and you'll see a timer icon in your system tray (top bar).

## Usage

### Adding a Timer

1. Click the timer icon in the system tray
2. Select "Add Timer"
3. Enter a title for your timer
4. Set the duration (hours, minutes, seconds)
5. Click "Start Timer"

### Viewing Active Timers

1. Click the timer icon
2. Select "View Timers"
3. See all running timers with real-time countdown
4. Click "Delete" next to any timer to remove it

### Timer Completion

When a timer reaches zero:
- A desktop notification appears with the timer's name
- An alert sound plays (or system beep if no sound file)
- The timer is automatically removed from the list

## Customization

### Custom Icon

Place a PNG image (24x24 or 32x32 pixels) at:
```
resources/icons/timer-icon.png
```

If not provided, the system's "alarm-clock" icon is used.

### Custom Alert Sound

Place an OGG audio file at:
```
resources/sounds/alert.ogg
```

If not provided, a system beep is used.

## Project Structure

```
timer_app/
├── __init__.py
├── main.py                      # Application entry point
├── app.py                       # Main TimerApp class
├── timer_model.py               # Timer and TimerManager
├── timer_thread.py              # Background countdown threads
├── notifications.py             # Desktop notifications
├── utils.py                     # Helper functions
└── ui/
    ├── __init__.py
    ├── add_timer_dialog.py     # Add timer dialog
    ├── view_timers_dialog.py   # View timers dialog
    └── menu_builder.py         # System tray menu

resources/
├── icons/                       # Custom icon location
└── sounds/                      # Custom sound location
```

## Troubleshooting

### Application doesn't appear in system tray

- Make sure you have AppIndicator3 installed: `gir1.2-appindicator3-0.1`
- Try logging out and back in
- Check that your desktop environment supports system tray icons

### Notifications don't appear

- Ensure libnotify is installed: `gir1.2-notify-0.7`
- Check your system notification settings
- The app will print to console as a fallback

### Sound doesn't play

- Install audio dependencies: `sudo apt-get install libcanberra-gtk3-module`
- The app will fall back to system beep if sound playback fails
- Check that your system audio is working

### Import errors

Make sure all system dependencies are installed:
```bash
sudo apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
```

## Technical Details

- **Language**: Python 3
- **GUI Framework**: GTK 3 (via PyGObject)
- **System Tray**: AppIndicator3
- **Notifications**: libnotify (notify2)
- **Threading**: Python threading module for concurrent timers

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Requirements Document

See [timer-app-requirements.md](timer-app-requirements.md) for the complete requirements specification.
