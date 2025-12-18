import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3
from timer_app.timer_model import TimerManager
from timer_app.notifications import NotificationHandler
from timer_app.ui.menu_builder import MenuBuilder
from timer_app.ui.add_timer_dialog import AddTimerDialog
from timer_app.ui.view_timers_dialog import ViewTimersDialog


class TimerApp:
    """Main application class for the multi-timer system tray app."""

    def __init__(self):
        """Initialize the timer application."""
        self.timer_manager = TimerManager()
        self.notification_handler = NotificationHandler()
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

    def show_add_timer_dialog(self):
        """Show the dialog to add a new timer."""
        dialog = AddTimerDialog(None)
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

    def quit(self):
        """Quit the application gracefully."""
        self.timer_manager.shutdown()
        Gtk.main_quit()

    def run(self):
        """Run the application main loop."""
        Gtk.main()
