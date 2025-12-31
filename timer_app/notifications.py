import os
import sys
import subprocess
import threading
import time


class LoopingSoundPlayer:
    """Plays a sound in a loop until stopped."""

    def __init__(self, sound_method, sound_path=None, playsound_func=None):
        """Initialize the looping sound player.

        Args:
            sound_method: Sound method to use ('playsound', 'canberra', 'paplay', 'beep')
            sound_path: Path to sound file (for playsound/paplay methods)
            playsound_func: The playsound function (for playsound method)
        """
        self.sound_method = sound_method
        self.sound_path = sound_path
        self.playsound_func = playsound_func
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        """Start looping the sound."""
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the looping sound."""
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=1)

    def _loop(self):
        """Sound loop runner."""
        while not self.stop_event.is_set():
            self._play_once()
            # Wait between plays (~3 seconds), checking stop_event frequently
            for _ in range(30):
                if self.stop_event.is_set():
                    return
                time.sleep(0.1)

    def _play_once(self):
        """Play the sound once."""
        try:
            if self.sound_method == 'playsound' and self.playsound_func:
                self.playsound_func(self.sound_path, block=True)
            elif self.sound_method == 'canberra':
                subprocess.run(
                    ['canberra-gtk-play', '-i', 'complete', '-d', 'Timer Alarm'],
                    capture_output=True,
                    timeout=5
                )
            elif self.sound_method == 'paplay' and self.sound_path:
                subprocess.run(
                    ['paplay', self.sound_path],
                    capture_output=True,
                    timeout=5
                )
            elif self.sound_method == 'beep':
                print("\a", end="", flush=True)
        except Exception as e:
            print(f"Error playing sound: {e}")


class NotificationHandler:
    """Handles desktop notifications and sound alerts for timer completion."""

    def __init__(self):
        """Initialize the notification handler."""
        self.notify_available = False
        self.sound_available = False
        self.sound_path = None
        self.sound_method = None
        self.alarm_callback = None  # Callback for creating snooze timers

        self._init_notifications()
        self._init_sound()

    def set_alarm_callback(self, callback):
        """Set callback for alarm-related actions (like creating snooze timers).

        Args:
            callback: Function(title, snooze_seconds, timer_type) to create a snooze timer
        """
        self.alarm_callback = callback

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
        # Try multiple sound methods in order of preference

        # 1. Try custom sound file with playsound
        try:
            from playsound import playsound
            self.playsound = playsound
            sound_file = self._find_sound_file()
            if sound_file and os.path.exists(sound_file):
                self.sound_path = sound_file
                self.sound_method = 'playsound'
                self.sound_available = True
                print("Using custom alert sound")
                return
        except Exception as e:
            print(f"Note: playsound not available: {e}")

        # 2. Try canberra-gtk-play (GNOME notification sounds)
        if self._check_command_exists('canberra-gtk-play'):
            self.sound_method = 'canberra'
            self.sound_available = True
            print("Using system notification sound (canberra)")
            return

        # 3. Try paplay with system sounds
        if self._check_command_exists('paplay'):
            # Check for common system alert sounds
            for sound_path in [
                '/usr/share/sounds/freedesktop/stereo/complete.oga',
                '/usr/share/sounds/freedesktop/stereo/bell.oga',
                '/usr/share/sounds/ubuntu/stereo/message.ogg',
                '/usr/share/sounds/ubuntu/stereo/bell.ogg'
            ]:
                if os.path.exists(sound_path):
                    self.sound_path = sound_path
                    self.sound_method = 'paplay'
                    self.sound_available = True
                    print(f"Using system sound: {sound_path}")
                    return

        # 4. Fallback to system beep
        print("No sound system available, will use system beep")
        self.sound_method = 'beep'
        self.sound_available = True

    def _check_command_exists(self, command):
        """Check if a command exists in the system.

        Args:
            command: Command name to check

        Returns:
            True if command exists, False otherwise
        """
        try:
            subprocess.run(['which', command],
                         capture_output=True,
                         check=True,
                         timeout=1)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False

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
        if hasattr(timer, 'timer_type') and timer.timer_type == "alarm":
            self._show_alarm_popup(timer)
        else:
            self._show_notification(timer)
            self._play_sound()

    def _show_alarm_popup(self, timer):
        """Show persistent alarm popup with looping sound.

        Args:
            timer: The completed Timer object
        """
        from timer_app.ui.alarm_dialog import AlarmDialog

        # Create looping sound player
        sound_player = None
        if self.sound_available:
            sound_player = LoopingSoundPlayer(
                self.sound_method,
                self.sound_path,
                getattr(self, 'playsound', None)
            )
            sound_player.start()

        def on_stop(timer):
            """Handle stop button."""
            pass  # Timer already completed, just close

        def on_snooze(timer, snooze_seconds):
            """Handle snooze - create a new alarm timer."""
            if self.alarm_callback:
                self.alarm_callback(timer.title, snooze_seconds, "alarm")

        # Show alarm dialog
        dialog = AlarmDialog(
            timer,
            sound_player,
            on_stop,
            on_snooze
        )
        dialog.show_all()

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
        if not self.sound_available:
            return

        try:
            if self.sound_method == 'playsound':
                # Custom sound file with playsound
                self.playsound(self.sound_path, block=False)
            elif self.sound_method == 'canberra':
                # GNOME notification sound
                subprocess.Popen(
                    ['canberra-gtk-play', '-i', 'complete', '-d', 'Timer Complete'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            elif self.sound_method == 'paplay':
                # System sound file with paplay
                subprocess.Popen(
                    ['paplay', self.sound_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            elif self.sound_method == 'beep':
                # Fallback to system beep
                self._system_beep()
        except Exception as e:
            print(f"Error playing sound: {e}")
            self._system_beep()

    def _system_beep(self):
        """Fallback to system beep."""
        try:
            print("\a", end="", flush=True)
        except Exception:
            pass
