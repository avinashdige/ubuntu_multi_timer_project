import os
import sys


class NotificationHandler:
    """Handles desktop notifications and sound alerts for timer completion."""

    def __init__(self):
        """Initialize the notification handler."""
        self.notify_available = False
        self.sound_available = False
        self.sound_path = None

        self._init_notifications()
        self._init_sound()

    def _init_notifications(self):
        """Initialize the notification system."""
        try:
            import notify2
            notify2.init("Multi-Timer App")
            self.notify_available = True
            self.notify2 = notify2
        except Exception as e:
            print(f"Warning: Could not initialize notifications: {e}")
            self.notify_available = False

    def _init_sound(self):
        """Initialize sound playback."""
        try:
            from playsound import playsound
            self.playsound = playsound
            self.sound_available = True

            sound_file = self._find_sound_file()
            if sound_file and os.path.exists(sound_file):
                self.sound_path = sound_file
            else:
                print("Warning: Alert sound file not found, will use system beep")
        except Exception as e:
            print(f"Warning: Could not initialize sound playback: {e}")
            self.sound_available = False

    def _find_sound_file(self):
        """Find the alert sound file.

        Returns:
            Path to sound file or None
        """
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        sound_path = os.path.join(base_path, "resources", "sounds", "alert.ogg")
        return sound_path

    def notify_timer_complete(self, timer):
        """Show notification and play sound when timer completes.

        Args:
            timer: The completed Timer object
        """
        self._show_notification(timer)
        self._play_sound()

    def _show_notification(self, timer):
        """Display desktop notification.

        Args:
            timer: The completed Timer object
        """
        if self.notify_available:
            try:
                notification = self.notify2.Notification(
                    "Timer Complete",
                    f"{timer.title} has finished!",
                    "dialog-information"
                )
                notification.set_urgency(self.notify2.URGENCY_NORMAL)
                notification.set_timeout(5000)
                notification.show()
            except Exception as e:
                print(f"Error showing notification: {e}")
                self._fallback_notification(timer)
        else:
            self._fallback_notification(timer)

    def _fallback_notification(self, timer):
        """Fallback notification using console output.

        Args:
            timer: The completed Timer object
        """
        print(f"\n*** TIMER COMPLETE: {timer.title} ***\n")

    def _play_sound(self):
        """Play alert sound."""
        if self.sound_available and self.sound_path and os.path.exists(self.sound_path):
            try:
                self.playsound(self.sound_path, block=False)
            except Exception as e:
                print(f"Error playing sound: {e}")
                self._system_beep()
        else:
            self._system_beep()

    def _system_beep(self):
        """Fallback to system beep."""
        try:
            print("\a", end="", flush=True)
        except Exception:
            pass
