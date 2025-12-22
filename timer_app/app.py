import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GLib
from timer_app.timer_model import TimerManager
from timer_app.notifications import NotificationHandler
from timer_app.timer_history import TimerHistory
from timer_app.timer_presets import TimerPresets
from timer_app.ui.menu_builder import MenuBuilder
from timer_app.ui.add_timer_dialog import AddTimerDialog
from timer_app.ui.view_timers_dialog import ViewTimersDialog


class TimerApp:
    """Main application class for the multi-timer system tray app."""

    def __init__(self):
        """Initialize the timer application."""
        self.timer_manager = TimerManager()
        self.notification_handler = NotificationHandler()
        self.timer_history = TimerHistory()
        self.timer_presets = TimerPresets()
        self.timer_manager.set_notification_handler(self.notification_handler)

        self.indicator = AppIndicator3.Indicator.new(
            "multi-timer-app",
            "alarm-clock",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.menu_builder = MenuBuilder(self)
        menu = self.menu_builder.build_menu()
        self.indicator.set_menu(menu)

        self.view_dialog = None

        self.label_update_timeout_id = None

        # Register for pin change notifications
        self.timer_manager.add_pin_change_callback(self.on_pin_changed)

        # Start label update loop (1 second interval)
        self.label_update_timeout_id = GLib.timeout_add(1000, self.update_indicator_label)

        # Initial label update
        self.update_indicator_label()

        # Initialize DBus service for CLI support
        self.dbus_service = None
        self._init_dbus_service()

    def _init_dbus_service(self):
        """Initialize the DBus service for CLI communication."""
        try:
            from timer_app.dbus_service import TimerAppDBusService
            self.dbus_service = TimerAppDBusService(self)
            print("DBus service initialized - CLI support enabled")
        except Exception as e:
            print(f"Warning: Could not initialize DBus service: {e}")
            print("CLI support will not be available")

    def show_add_timer_dialog(self):
        """Show the dialog to add a new timer."""
        dialog = AddTimerDialog(None, self.timer_history.get_titles())
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            timer_data = dialog.get_timer_data()
            if timer_data:
                try:
                    self.timer_manager.add_timer(
                        timer_data["title"],
                        timer_data["hours"],
                        timer_data["minutes"],
                        timer_data["seconds"]
                    )
                    # Save the title to history
                    self.timer_history.add_title(timer_data["title"])
                except Exception as e:
                    print(f"Error creating timer: {e}")

        dialog.destroy()

    def show_view_timers_dialog(self):
        """Show the dialog to view all active timers."""
        if self.view_dialog is None or not self.view_dialog.get_visible():
            self.view_dialog = ViewTimersDialog(None, self.timer_manager)
            self.view_dialog.show()
        else:
            self.view_dialog.present()

    def start_preset_timer(self, preset):
        """Start a timer from a preset.

        Args:
            preset: Dictionary with keys: title, hours, minutes, seconds
        """
        try:
            self.timer_manager.add_timer(
                preset["title"],
                preset["hours"],
                preset["minutes"],
                preset["seconds"]
            )
            # Save to history
            self.timer_history.add_title(preset["title"])
        except Exception as e:
            print(f"Error starting preset timer: {e}")

    def update_indicator_label(self):
        """Update the AppIndicator label with pinned timer countdown.

        Returns:
            True to continue the timeout callback
        """
        pinned_timer = self.timer_manager.get_pinned_timer()

        if pinned_timer:
            # Format: "HH:MM:SS Title..."
            from timer_app.utils import format_time
            time_str = format_time(pinned_timer.remaining_seconds)

            # Truncate title to fit - aim for ~25 char total display
            # "00:00:00 " = 9 chars, leave ~16 for title
            max_title_length = 16
            title = pinned_timer.title
            if len(title) > max_title_length:
                title = title[:max_title_length - 3] + "..."

            label_text = f"{time_str} {title}"

            # Guide string ensures consistent spacing (prevents jitter)
            # Use maximum possible width: "99:59:59 " + max title
            guide_str = "99:59:59 " + "M" * max_title_length

            self.indicator.set_label(label_text, guide_str)
        else:
            # No timers - hide label completely
            self.indicator.set_label("", "")

        return True  # Continue timeout

    def on_pin_changed(self):
        """Callback when the pinned timer changes.

        Triggers an immediate label update.
        """
        self.update_indicator_label()

    def quit(self):
        """Quit the application gracefully."""
        # Stop label updates
        if self.label_update_timeout_id:
            GLib.source_remove(self.label_update_timeout_id)
            self.label_update_timeout_id = None

        self.timer_manager.shutdown()
        Gtk.main_quit()

    def run(self):
        """Run the application main loop."""
        Gtk.main()
