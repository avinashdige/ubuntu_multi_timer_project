import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GLib
from datetime import datetime

from timer_app.timer_model import TimerManager
from timer_app.notifications import NotificationHandler
from timer_app.timer_history import TimerHistory
from timer_app.timer_presets import TimerPresets
from timer_app.ui.menu_builder import MenuBuilder
from timer_app.ui.add_timer_dialog import AddTimerDialog
from timer_app.ui.view_timers_dialog import ViewTimersDialog

# Tracker imports
from timer_app.tracker.manager import TrackerManager
from timer_app.tracker.db import TrackerDB
from timer_app.ui.start_activity_dialog import StartActivityDialog
from timer_app.ui.dashboard_dialog import DashboardDialog
# Import format_tracker_duration
from timer_app.utils import format_tracker_duration


class TimerApp:
    """Main application class for the multi-timer system tray app."""

    def __init__(self):
        """Initialize the timer application."""
        self.timer_manager = TimerManager()
        self.tracker_manager = TrackerManager()
        
        self.notification_handler = NotificationHandler()
        self.timer_history = TimerHistory()
        self.timer_presets = TimerPresets()
        self.timer_manager.set_notification_handler(self.notification_handler)

        # Set up alarm callback for snooze functionality
        self.notification_handler.set_alarm_callback(self._create_snooze_timer)

        self.indicator = AppIndicator3.Indicator.new(
            "multi-timer-app",
            "alarm-clock",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        # List to hold active tracker menu items for live updates
        self.active_session_items = []

        self.menu_builder = MenuBuilder(self)
        self.refresh_menu()

        self.view_dialog = None
        self.dashboard_dialog = None

        self.label_update_timeout_id = None

        # Register for pin change notifications
        self.timer_manager.add_pin_change_callback(self.on_state_changed)
        self.tracker_manager.add_state_change_callback(self.on_state_changed)

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

    def refresh_menu(self):
        """Rebuild and set the system tray menu."""
        menu = self.menu_builder.build_menu()
        self.indicator.set_menu(menu)

    def show_add_timer_dialog(self):
        """Show the dialog to add a new timer."""
        dialog = AddTimerDialog(None, timer_history=self.timer_history)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            timer_data = dialog.get_timer_data()
            if timer_data:
                try:
                    self.timer_manager.add_timer(
                        timer_data["title"],
                        timer_data["hours"],
                        timer_data["minutes"],
                        timer_data["seconds"],
                        timer_type=timer_data.get("timer_type", "timer")
                    )
                    # Save the title and duration to history
                    self.timer_history.add_title(
                        timer_data["title"],
                        hours=timer_data["hours"],
                        minutes=timer_data["minutes"],
                        seconds=timer_data["seconds"]
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
            
    def show_start_activity_dialog(self):
        """Show the dialog to start a tracker activity."""
        recent = self.tracker_manager.get_recent_tasks()
        dialog = StartActivityDialog(None, recent_tasks=recent)
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            task_name = dialog.get_task_name()
            if task_name:
                self.tracker_manager.start_task(task_name)
        
        dialog.destroy()
        
    def show_dashboard(self):
        """Show the daily report dashboard."""
        if self.dashboard_dialog is None or not self.dashboard_dialog.get_visible():
            self.dashboard_dialog = DashboardDialog(self.tracker_manager)
            self.dashboard_dialog.show_all()
        else:
            self.dashboard_dialog.present()
            self.dashboard_dialog.refresh_data(None)

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
            # Save to history with duration
            self.timer_history.add_title(
                preset["title"],
                hours=preset["hours"],
                minutes=preset["minutes"],
                seconds=preset["seconds"]
            )
        except Exception as e:
            print(f"Error starting preset timer: {e}")

    def _create_snooze_timer(self, title, snooze_seconds, timer_type):
        """Create a snooze timer.

        Args:
            title: Original timer title
            snooze_seconds: Duration in seconds
            timer_type: Timer type (should be "alarm" for snooze)
        """
        hours = snooze_seconds // 3600
        minutes = (snooze_seconds % 3600) // 60
        seconds = snooze_seconds % 60

        try:
            self.timer_manager.add_timer(
                title,
                hours,
                minutes,
                seconds,
                timer_type=timer_type
            )
        except Exception as e:
            print(f"Error creating snooze timer: {e}")

    def update_indicator_label(self):
        """Update the AppIndicator label with timer/tracker status.

        Returns:
            True to continue the timeout callback
        """
        from timer_app.utils import format_time
        
        label_parts = []
        guide_parts = []
        
        # 1. Pinned Countdown Timer
        pinned_timer = self.timer_manager.get_pinned_timer()
        if pinned_timer:
            time_str = format_time(pinned_timer.remaining_seconds)
            
            # Truncate title
            max_title_length = 16
            title = pinned_timer.title
            if len(title) > max_title_length:
                title = title[:max_title_length - 3] + "..."
                
            label_parts.append(f"{time_str} {title}")
            guide_parts.append("99:59:59 " + "M" * max_title_length)

        # 2. Active Trackers
        active_sessions = self.tracker_manager.get_active_sessions()
        if active_sessions:
            if pinned_timer:
                # Combined View: "00:05 | 2 Active"
                label_parts.append(f"| {len(active_sessions)} Active")
                guide_parts.append("| 9 Active")
            else:
                # Tracker Only View: "Task Name (HH:MM) +1"
                # Find longest running session
                now = datetime.now()
                longest_session = None
                max_duration = -1
                
                for s in active_sessions:
                    current_duration = (now - s['start_time']).total_seconds()
                    total_duration = current_duration + s.get('accumulated_seconds', 0)
                    
                    if total_duration > max_duration:
                        max_duration = total_duration
                        longest_session = s
                
                if longest_session:
                    time_str = format_tracker_duration(max_duration)
                    
                    name = longest_session['task_name']
                    # Truncate
                    if len(name) > 15:
                        name = name[:12] + "..."
                        
                    text = f"{name} ({time_str})"
                    
                    if len(active_sessions) > 1:
                        text += f" +{len(active_sessions)-1}"
                        
                    label_parts.append(text)
                    guide_parts.append("M"*15 + " (99:99:99) +9")

        # Set final label
        if label_parts:
            label_text = " ".join(label_parts)
            guide_str = " ".join(guide_parts)
            self.indicator.set_label(label_text, guide_str)
        else:
            self.indicator.set_label("", "")

        # 3. Update Active Menu Items (Live ticking in menu)
        # Check if list is not empty
        if hasattr(self, 'active_session_items') and self.active_session_items:
            now = datetime.now()
            for item, session in self.active_session_items:
                try:
                    current_duration = (now - session['start_time']).total_seconds()
                    total_duration = current_duration + session.get('accumulated_seconds', 0)
                    time_str = format_tracker_duration(total_duration)
                    
                    # Update the label
                    item.set_label(f" [ ■ ] {session['task_name']} ({time_str})")
                except Exception:
                    # Handle potential race conditions or invalid widgets
                    pass

        return True  # Continue timeout

    def on_state_changed(self):
        """Callback when timers or trackers change state."""
        self.refresh_menu()
        self.update_indicator_label()

    def quit(self):
        """Quit the application gracefully."""
        # Stop label updates
        if self.label_update_timeout_id:
            GLib.source_remove(self.label_update_timeout_id)
            self.label_update_timeout_id = None

        self.timer_manager.shutdown()
        # Tracker DB handles its own connections, no specific shutdown needed
        Gtk.main_quit()

    def run(self):
        """Run the application main loop."""
        Gtk.main()