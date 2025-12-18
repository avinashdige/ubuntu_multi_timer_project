#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

import signal
import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from timer_app.app import TimerApp


def main():
    """Main entry point for the multi-timer application."""
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = TimerApp()

    try:
        print("Multi-Timer application started.")
        print("Look for the timer icon in your system tray!")
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        app.quit()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
