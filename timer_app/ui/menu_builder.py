import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from datetime import datetime
from timer_app.utils import format_tracker_duration

class MenuBuilder:
    """Builds the system tray menu for the timer application."""

    def __init__(self, app):
        """Initialize the menu builder.

        Args:
            app: Reference to the TimerApp instance
        """
        self.app = app

    def build_menu(self):
        """Build and return the system tray menu.

        Returns:
            Gtk.Menu object
        """
        # Clear previous active items tracking
        self.app.active_session_items = []
        
        menu = Gtk.Menu()

        # --- Time Tracker Section ---
        
        # Header
        tracker_header = Gtk.MenuItem(label="Time Tracker")
        tracker_header.set_sensitive(False)
        menu.append(tracker_header)
        
        # Active Sessions
        active_sessions = self.app.tracker_manager.get_active_sessions()
        now = datetime.now()
        
        if active_sessions:
            for session in active_sessions:
                current_duration = (now - session['start_time']).total_seconds()
                total_duration = current_duration + session.get('accumulated_seconds', 0)
                time_str = format_tracker_duration(total_duration)
                
                label = f" [ ■ ] {session['task_name']} ({time_str})"
                item = Gtk.MenuItem(label=label)
                item.connect("activate", lambda _, s=session: self.app.tracker_manager.stop_task(s['id']))
                menu.append(item)
                
                # Track this item for live updates
                self.app.active_session_items.append((item, session))
        else:
            empty_item = Gtk.MenuItem(label="  (No active tasks)")
            empty_item.set_sensitive(False)
            menu.append(empty_item)

        # Separator
        menu.append(Gtk.SeparatorMenuItem())
        
        # Recent/Paused Tasks
        recent_tasks = self.app.tracker_manager.get_recent_tasks()
        if recent_tasks:
            for task in recent_tasks:
                label = f" [ ▶ ] {task['name']}"
                item = Gtk.MenuItem(label=label)
                item.connect("activate", lambda _, t=task: self.app.tracker_manager.start_task(t['name']))
                menu.append(item)
            
            menu.append(Gtk.SeparatorMenuItem())

        # Tracker Actions
        start_item = Gtk.MenuItem(label="Start New Activity...")
        start_item.connect("activate", lambda _: self.app.show_start_activity_dialog())
        menu.append(start_item)
        
        dash_item = Gtk.MenuItem(label="Daily Dashboard...")
        dash_item.connect("activate", lambda _: self.app.show_dashboard())
        menu.append(dash_item)

        # --- Countdown Timer Section ---
        menu.append(Gtk.SeparatorMenuItem())
        
        timer_header = Gtk.MenuItem(label="Countdown Timers")
        timer_header.set_sensitive(False)
        menu.append(timer_header)

        # Add Timer with submenu
        add_item = Gtk.MenuItem(label="Add Timer")
        add_submenu = self._build_add_timer_submenu()
        add_item.set_submenu(add_submenu)
        menu.append(add_item)

        view_item = Gtk.MenuItem(label="View Timers")
        view_item.connect("activate", lambda _: self.app.show_view_timers_dialog())
        menu.append(view_item)

        # --- System ---
        menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", lambda _: self.app.quit())
        menu.append(quit_item)

        menu.show_all()
        return menu

    def _build_add_timer_submenu(self):
        """Build the submenu for adding timers.

        Returns:
            Gtk.Menu object with preset and quick timers
        """
        submenu = Gtk.Menu()

        # Custom timer option (opens dialog)
        custom_item = Gtk.MenuItem(label="Custom Timer...")
        custom_item.connect("activate", lambda _: self.app.show_add_timer_dialog())
        submenu.append(custom_item)

        # Separator
        submenu.append(Gtk.SeparatorMenuItem())

        # Quick timers section
        quick_label = Gtk.MenuItem(label="Quick Timers")
        quick_label.set_sensitive(False)
        submenu.append(quick_label)

        quick_timers = self.app.timer_presets.get_quick_timers()
        for timer in quick_timers:
            item = Gtk.MenuItem(label=f"  {timer['minutes']} min")
            item.connect("activate", lambda _, t=timer: self.app.start_preset_timer(t))
            submenu.append(item)

        # Separator
        submenu.append(Gtk.SeparatorMenuItem())

        # Preset timers section
        presets = self.app.timer_presets.get_presets()
        if presets:
            preset_label = Gtk.MenuItem(label="Preset Timers")
            preset_label.set_sensitive(False)
            submenu.append(preset_label)

            for preset in presets:
                # Format the duration
                duration_parts = []
                if preset['hours'] > 0:
                    duration_parts.append(f"{preset['hours']}h")
                if preset['minutes'] > 0:
                    duration_parts.append(f"{preset['minutes']}m")
                if preset['seconds'] > 0:
                    duration_parts.append(f"{preset['seconds']}s")
                duration_str = " ".join(duration_parts) if duration_parts else "0s"

                item = Gtk.MenuItem(label=f"  {preset['title']} ({duration_str})")
                item.connect("activate", lambda _, p=preset: self.app.start_preset_timer(p))
                submenu.append(item)

        return submenu