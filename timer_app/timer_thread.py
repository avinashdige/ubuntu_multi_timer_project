import time
import threading
import gi
gi.require_version('GLib', '2.0')
from gi.repository import GLib


class TimerThread(threading.Thread):
    """Thread that counts down a timer in the background."""

    def __init__(self, timer, callback):
        """Initialize the timer thread.

        Args:
            timer: Timer object to count down
            callback: Function to call when timer completes (called on main thread)
        """
        super().__init__(daemon=True)
        self.timer = timer
        self.callback = callback
        self.stop_event = threading.Event()

    def run(self):
        """Execute the countdown loop."""
        try:
            while self.timer.remaining_seconds > 0 and not self.stop_event.is_set():
                time.sleep(1)
                if not self.stop_event.is_set():
                    self.timer.remaining_seconds -= 1

            if self.timer.remaining_seconds == 0 and not self.stop_event.is_set():
                GLib.idle_add(self.callback, self.timer)
        except Exception as e:
            print(f"Error in timer thread for '{self.timer.title}': {e}")

    def stop(self):
        """Signal the thread to stop gracefully."""
        self.stop_event.set()
