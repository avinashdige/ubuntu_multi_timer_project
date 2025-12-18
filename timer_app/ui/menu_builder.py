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

        add_item = Gtk.MenuItem(label="Add Timer")
        add_item.connect("activate", lambda _: self.app.show_add_timer_dialog())
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
