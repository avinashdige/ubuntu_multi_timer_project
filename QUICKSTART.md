# Quick Start Guide

## Installation Complete! ✅

Your multi-timer application is ready to use.

## Running the Application

### Option 1: Using the run script (easiest)
```bash
./run.sh
```

### Option 2: Manual activation
```bash
source venv/bin/activate
python3 timer_app/main.py
```

**Important Notes:**
- The application runs in the background (system tray)
- You'll see console output: "Multi-Timer application started."
- Look for the timer icon in your Ubuntu top bar
- The terminal will stay open while the app runs
- To close the app, click the icon and select "Quit" or press Ctrl+C in the terminal

## What to Expect

1. **System Tray Icon**: Look for a clock/alarm icon in your Ubuntu top bar
2. **First Use**: Click the icon to see the menu with "Add Timer" and "View Timers"

## Testing the App

### Quick Test:
1. Click the system tray icon
2. Select "Add Timer"
3. Enter:
   - Title: "Test"
   - Duration: 0 hours, 0 minutes, 10 seconds
4. Click "Start Timer"
5. Click the icon again and select "View Timers"
6. Watch the countdown!
7. After 10 seconds, you'll get a notification

## Troubleshooting

### "Icon doesn't appear in system tray"
- **Solution**: Check if AppIndicator3 is installed:
  ```bash
  dpkg -l | grep appindicator3
  ```
  If not found, install it:
  ```bash
  sudo apt-get install gir1.2-appindicator3-0.1
  ```

### "No notifications"
- **Solution**: The app will print to console as fallback
- Check notification settings in Ubuntu

### "No sound"
- **Solution**: The app falls back to system beep
- To add a custom sound, place an `alert.ogg` file in `resources/sounds/`

## Current Status

✅ All core files implemented
✅ Dependencies installed
✅ System packages verified
✅ Ready to run!

## Next Steps

- **Customize**: Add custom icon to `resources/icons/timer-icon.png`
- **Add Sound**: Place alert sound at `resources/sounds/alert.ogg`
- **Auto-start**: Add to startup applications if desired

---

For detailed information, see [README.md](README.md)
