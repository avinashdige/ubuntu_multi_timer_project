# GEMINI.md - Developer Onboarding & Architecture Guide

## 1. Project Overview

**Project Name:** Ubuntu Multi-Timer Project
**Platform:** Ubuntu Linux (Desktop)
**Frameworks:** Python 3, GTK 3 (PyGObject), AppIndicator3

This application is a system tray utility for Ubuntu that manages multiple countdown timers simultaneously. It integrates deeply with the Linux desktop environment using AppIndicators, Libnotify notifications, and DBus.

## 2. Directory Structure

```
/
├── timer_app/                 # Source Code Package
│   ├── main.py                # Entry point
│   ├── app.py                 # Main Application Class (TimerApp)
│   ├── timer_model.py         # Core Logic (TimerManager, Timer)
│   ├── timer_thread.py        # Background countdown threads
│   ├── notifications.py       # Notification handling (notify2)
│   ├── dbus_service.py        # IPC for CLI control
│   └── ui/                    # User Interface
│       ├── menu_builder.py    # System tray menu construction
│       ├── add_timer_dialog.py # GTK Dialog for creation
│       └── view_timers_dialog.py # GTK Dialog for management
├── resources/                 # Assets (Icons, Sounds)
├── data/                      # Persistent storage (logs)
├── requirements.txt           # Python dependencies
├── install.sh                 # Installation script
├── install_desktop.sh         # Desktop integration script
└── DEADLOCK_FIX.md            # Critical architectural documentation
```

## 3. Architecture

### 3.1 Core Components

*   **`TimerApp` (`timer_app/app.py`):** The central controller. Initializes the GTK application, system tray indicator (`AppIndicator3`), and connects the `TimerManager` to the UI.
*   **`TimerManager` (`timer_app/timer_model.py`):** The "Brain". Manages the lifecycle of all timers, handles thread safety, and orchestrates the "Pinned Timer" logic (displaying the soonest timer in the tray).
*   **`TimerThread` (`timer_app/timer_thread.py`):** A dedicated `threading.Thread` for each active timer. It performs the countdown and signals completion via `GLib.idle_add` to ensure thread safety when updating the UI.

### 3.2 Concurrency & Threading Model

*   **Multithreading:** The app uses the standard `threading` library. Each timer runs in its own thread (`daemon=True`).
*   **Main Loop:** The GUI runs on the main thread (GTK Main Loop).
*   **Inter-Thread Communication:**
    *   **Background to Main:** `TimerThread` uses `GLib.idle_add(callback)` to execute code on the main thread when a timer finishes. This avoids GTK threading violations.
    *   **Main to Background:** The main thread controls timers via `TimerManager`, which uses `threading.Lock` to protect shared state (`self.timers` dict).

### 3.3 Critical: Deadlock Prevention

See `DEADLOCK_FIX.md` for detailed rules.
1.  **Release-Before-Notify:** Never invoke external callbacks (like UI updates) while holding the `TimerManager` lock. State changes happen inside the lock, but notifications occur *after* the lock is released.
2.  **Internal Unlocked Helpers:** Use `_method_unlocked()` helpers for internal logic to avoid reentrant lock attempts (e.g., `_get_earliest_timer_unlocked` vs `get_earliest_timer`).

### 3.4 Integration

*   **System Tray:** Uses `gi.repository.AppIndicator3`.
*   **Notifications:** Uses `notify2` (libnotify wrapper) for desktop popups.
*   **Audio:** Uses `playsound` (via GStreamer/AppKit depending on OS, or system beep as fallback).
*   **CLI Control:** A DBus service allows command-line interaction with the running GUI instance.

## 4. Coding Conventions

*   **Language:** Python 3.10+
*   **Style:** PEP 8 compliance generally expected.
    *   Variables/Functions: `snake_case`
    *   Classes: `CamelCase`
*   **Imports:** Explicit `gi.require_version` calls are mandatory before importing GTK/AppIndicator modules.
*   **Path Handling:** `utils.py` provides helpers. Absolute paths derived from `__file__` are preferred over relative paths to ensure stability when run from different contexts (system service vs local run).

## 5. Development Setup

### System Dependencies
The app requires system-level packages for GTK. `pip` alone is insufficient.
```bash
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
    gir1.2-appindicator3-0.1 gir1.2-notify-0.7 libcanberra-gtk3-module
```

### Environment
Use a virtual environment with system site packages enabled:
```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running Locally
```bash
./run.sh
```

## 6. Common Tasks

*   **Adding a Feature:**
    1.  Update `TimerManager` in `timer_model.py` if logic changes (mind the locks!).
    2.  Update UI in `timer_app/ui/`.
    3.  If adding a dependency, check if it's available via `apt` (preferred for GTK libs) or `pip`.

*   **Debugging:**
    *   Standard `print()` works and shows in the console when running via `./run.sh`.
    *   Check `DEADLOCK_FIX.md` if the app freezes.
