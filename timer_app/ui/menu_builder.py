import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


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
        menu = Gtk.Menu()

        # Add Timer with submenu
        add_item = Gtk.MenuItem(label="Add Timer")
        add_submenu = self._build_add_timer_submenu()
        add_item.set_submenu(add_submenu)
        menu.append(add_item)

        view_item = Gtk.MenuItem(label="View Timers")
        view_item.connect("activate", lambda _: self.app.show_view_timers_dialog())
        menu.append(view_item)

        separator = Gtk.SeparatorMenuItem()
        menu.append(separator)

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
