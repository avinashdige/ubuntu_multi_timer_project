import dbus
import dbus.service
import dbus.mainloop.glib


class TimerAppDBusService(dbus.service.Object):
    """DBus service for the timer application."""

    def __init__(self, timer_app):
        """Initialize the DBus service.

        Args:
            timer_app: The main TimerApp instance
        """
        self.timer_app = timer_app

        # Set up DBus
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        bus_name = dbus.service.BusName(
            'com.github.MultiTimerApp',
            bus=dbus.SessionBus()
        )

        super().__init__(bus_name, '/com/github/MultiTimerApp')

    @dbus.service.method(
        'com.github.MultiTimerApp',
        in_signature='siii',
        out_signature='b'
    )
    def AddTimer(self, title, hours, minutes, seconds):
        """Add a timer via DBus.

        Args:
            title: Timer title
            hours: Hours component
            minutes: Minutes component
            seconds: Seconds component

        Returns:
            True if successful, False otherwise
        """
        try:
            self.timer_app.timer_manager.add_timer(
                title, hours, minutes, seconds
            )
            # Save to history
            self.timer_app.timer_history.add_title(title)
            return True
        except Exception as e:
            print(f"Error adding timer via DBus: {e}")
            return False

    @dbus.service.method(
        'com.github.MultiTimerApp',
        in_signature='',
        out_signature='a(sssi)'
    )
    def GetTimers(self):
        """Get all active timers.

        Returns:
            List of tuples (id, title, remaining_time_formatted, remaining_seconds)
        """
        try:
            from timer_app.utils import format_time
            timers = self.timer_app.timer_manager.get_all_timers()
            result = []
            for timer in timers:
                result.append((
                    str(timer.timer_id),
                    timer.title,
                    format_time(timer.remaining_seconds),
                    timer.remaining_seconds
                ))
            return result
        except Exception as e:
            print(f"Error getting timers via DBus: {e}")
            return []

    @dbus.service.method(
        'com.github.MultiTimerApp',
        in_signature='s',
        out_signature='b'
    )
    def DeleteTimer(self, timer_id):
        """Delete a timer via DBus.

        Args:
            timer_id: UUID of the timer to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.timer_app.timer_manager.delete_timer(timer_id)
            return True
        except Exception as e:
            print(f"Error deleting timer via DBus: {e}")
            return False
