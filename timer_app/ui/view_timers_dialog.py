import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from timer_app.utils import format_time


class ViewTimersDialog(Gtk.Dialog):
    """Dialog for viewing and managing all active timers."""

    def __init__(self, parent, timer_manager):
        """Initialize the view timers dialog.

        Args:
            parent: Parent window (can be None)
            timer_manager: TimerManager instance
        """
        super().__init__(
            title="Active Timers",
            transient_for=parent,
            flags=0,
            border_width=10
        )

        self.timer_manager = timer_manager
        self.timeout_id = None

        self.set_default_size(400, 300)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(200)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.listbox)

        box = self.get_content_area()
        box.pack_start(scrolled, True, True, 0)

        self.add_button("Close", Gtk.ResponseType.CLOSE)

        self.timeout_id = GLib.timeout_add(500, self.update_display)

        self.connect("response", self.on_response)
        self.connect("destroy", self.on_destroy)

        self.update_display()
        self.show_all()

    def update_display(self):
        """Update the list of timers with current countdown values.

        Returns:
            True to continue the timeout callback
        """
        for child in self.listbox.get_children():
            self.listbox.remove(child)

        timers = self.timer_manager.get_all_timers()

        if not timers:
            label = Gtk.Label(label="No active timers")
            label.set_margin_top(20)
            label.set_margin_bottom(20)
            self.listbox.add(label)
        else:
            for timer in sorted(timers, key=lambda t: t.created_at):
                row = self.create_timer_row(timer)
                self.listbox.add(row)

        self.listbox.show_all()
        return True

    def create_timer_row(self, timer):
        """Create a list row for a timer.

        Args:
            timer: Timer object

        Returns:
            Gtk.ListBoxRow
        """
        row = Gtk.ListBoxRow()
        row.set_activatable(False)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.set_margin_top(8)
        hbox.set_margin_bottom(8)
        hbox.set_margin_start(10)
        hbox.set_margin_end(10)

        title_label = Gtk.Label(label=timer.title)
        title_label.set_halign(Gtk.Align.START)
        title_label.set_ellipsize(3)
        title_label.set_max_width_chars(30)
        hbox.pack_start(title_label, True, True, 0)

        time_str = format_time(timer.remaining_seconds)
        time_label = Gtk.Label()
        time_label.set_markup(f'<span font_family="monospace" size="large">{time_str}</span>')
        time_label.set_halign(Gtk.Align.END)
        hbox.pack_start(time_label, False, False, 0)

        delete_btn = Gtk.Button(label="Delete")
        delete_btn.get_style_context().add_class("destructive-action")
        delete_btn.connect("clicked", self.on_delete_clicked, timer.id)
        hbox.pack_start(delete_btn, False, False, 0)

        row.add(hbox)
        return row

    def on_delete_clicked(self, button, timer_id):
        """Handle delete button click.

        Args:
            button: The button that was clicked
            timer_id: ID of timer to delete
        """
        self.timer_manager.delete_timer(timer_id)
        self.update_display()

    def on_response(self, dialog, response_id):
        """Handle dialog response.

        Args:
            dialog: This dialog instance
            response_id: Response type
        """
        self.destroy()

    def on_destroy(self, widget):
        """Clean up when dialog is destroyed.

        Args:
            widget: This dialog instance
        """
        if self.timeout_id:
            GLib.source_remove(self.timeout_id)
            self.timeout_id = None
