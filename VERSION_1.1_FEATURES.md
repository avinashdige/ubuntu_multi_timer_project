# Version 1.1 Features

This document describes the new features added in version 1.1 of the Multi-Timer application.

## 1. Auto-complete Timer Titles

The "Add Timer" dialog now includes auto-complete functionality for timer titles. As you type a timer name, the app will suggest previously used timer titles.

**How it works:**
- Timer titles are automatically saved to history when you create a timer
- History is stored in `~/.config/multi-timer-app/timer_history.json`
- Up to 50 most recent timer titles are remembered
- Suggestions appear as you type (after 1 character)

## 2. Command-Line Interface (CLI)

You can now manage timers from the command line using the `timer-cli` command.

**Installation:**
After running the installation script, the `timer-cli` command will be available system-wide.

**Commands:**

### Add a timer:
```bash
# 5 minute timer
timer-cli add "Coffee" 5m

# 1 hour 30 minutes
timer-cli add "Meeting" 1h30m

# With seconds
timer-cli add "Quick task" 2m30s

# Hours, minutes, and seconds
timer-cli add "Complex task" 1h30m45s
```

### List active timers:
```bash
timer-cli list
```

### Delete a timer:
```bash
timer-cli delete "Coffee"
```

**Requirements:**
- The Multi-Timer app must be running in the system tray
- Uses DBus for inter-process communication

## 3. Improved Sound Notifications

Sound notifications have been enhanced with multiple fallback methods:

1. **Custom sound file** (if `resources/sounds/alert.ogg` exists)
2. **System notification sound** via `canberra-gtk-play` (GNOME)
3. **System sound files** via `paplay` (PulseAudio)
4. **System beep** as final fallback

**Adding a custom sound:**
Place an OGG format sound file at `resources/sounds/alert.ogg`. The app will automatically use it.

## 4. Preset/Standard Timers

Define frequently-used timers that can be started with a single click from the system tray menu.

**Default Presets:**
- Quick Break (5 minutes)
- Coffee Break (10 minutes)
- Pomodoro (25 minutes)
- Short Meeting (30 minutes)
- Long Meeting (1 hour)

**Configuration:**
Presets are stored in `~/.config/multi-timer-app/timer_presets.json`

You can edit this file to add, remove, or modify presets. Example format:

```json
{
  "presets": [
    {
      "title": "My Custom Timer",
      "hours": 0,
      "minutes": 15,
      "seconds": 0
    }
  ]
}
```

**Accessing Presets:**
1. Click the system tray icon
2. Hover over "Add Timer"
3. Select a preset from the "Preset Timers" section

## 5. Quick Timer Buttons

Quick-access buttons for common timer durations are now available in the "Add Timer" submenu.

**Available Quick Timers:**
- 1 minute
- 2 minutes
- 3 minutes
- 4 minutes
- 5 minutes
- 7 minutes
- 10 minutes
- 12 minutes

**Usage:**
1. Click the system tray icon
2. Hover over "Add Timer"
3. Select a duration from the "Quick Timers" section

## System Tray Menu Structure

```
Multi-Timer App Icon
├─ Add Timer →
│  ├─ Custom Timer...
│  ├─────────────────
│  ├─ Quick Timers
│  │  ├─ 1 min
│  │  ├─ 2 min
│  │  ├─ 3 min
│  │  ├─ 4 min
│  │  ├─ 5 min
│  │  ├─ 7 min
│  │  ├─ 10 min
│  │  └─ 12 min
│  ├─────────────────
│  ├─ Preset Timers
│  │  ├─ Quick Break (5m)
│  │  ├─ Coffee Break (10m)
│  │  ├─ Pomodoro (25m)
│  │  ├─ Short Meeting (30m)
│  │  └─ Long Meeting (1h)
│
├─ View Timers
├─────────────────
└─ Quit
```

## Configuration Files

All configuration files are stored in `~/.config/multi-timer-app/`:

- `timer_history.json` - Timer title autocomplete history
- `timer_presets.json` - Preset timer configurations

## Upgrading from Version 1.0

All new features are backward compatible. Simply run the installation script again:

```bash
./install.sh
```

Your existing timer settings and history will be preserved.
