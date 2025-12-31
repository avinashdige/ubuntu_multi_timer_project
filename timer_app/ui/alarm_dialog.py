import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GLib', '2.0')
from gi.repository import Gtk, GLib
from datetime import datetime


class AlarmDialog(Gtk.Window):
    """Persistent alarm window that displays until dismissed."""

    STANDARD_SNOOZE_MINUTES = 5

    def __init__(self, timer, sound_player, on_stop_callback, on_snooze_callback):
        """Initialize the alarm dialog.

        Args:
            timer: The completed Timer object
            sound_player: LoopingSoundPlayer instance (or None)
            on_stop_callback: Called when Stop is clicked (receives timer)
            on_snooze_callback: Called when snooze is activated (receives timer, snooze_seconds)
        """
        super().__init__(title=f"Alarm: {timer.title}")

        self.timer = timer
        self.sound_player = sound_player
        self.on_stop_callback = on_stop_callback
        self.on_snooze_callback = on_snooze_callback
        self.completion_time = datetime.now()
        self.elapsed_timeout_id = None

        self._setup_window()
        self._setup_ui()
        self._start_elapsed_timer()

    def _setup_window(self):
        """Configure window properties."""
        self.set_default_size(400, 220)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_keep_above(True)
        self.set_urgency_hint(True)
        self.set_deletable(False)  # No close button
        self.set_resizable(False)
        self.connect("delete-event", self._on_delete_event)

    def _setup_ui(self):
        """Build the dialog UI."""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)

        # Timer title (large, bold)
        title_label = Gtk.Label()
        title_label.set_markup(
            f'<span size="x-large" weight="bold">{GLib.markup_escape_text(self.timer.title)}</span>'
        )
        main_box.pack_start(title_label, False, False, 0)

        # "Timer Complete!" message
        complete_label = Gtk.Label(label="Timer Complete!")
        main_box.pack_start(complete_label, False, False, 0)

        # Elapsed time label (updates every second)
        self.elapsed_label = Gtk.Label(label="Elapsed: 00:00:00")
        self.elapsed_label.set_margin_top(10)
        main_box.pack_start(self.elapsed_label, False, False, 0)

        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(15)

        # Stop button (primary action)
        stop_btn = Gtk.Button(label="Stop")
        stop_btn.get_style_context().add_class("destructive-action")
        stop_btn.set_size_request(100, 40)
        stop_btn.connect("clicked", self._on_stop_clicked)
        button_box.pack_start(stop_btn, False, False, 0)

        # Snooze 5 min button
        snooze_btn = Gtk.Button(label="Snooze 5 min")
        snooze_btn.set_size_request(110, 40)
        snooze_btn.connect("clicked", self._on_snooze_clicked)
        button_box.pack_start(snooze_btn, False, False, 0)

        # Snooze... button (custom duration)
        snooze_custom_btn = Gtk.Button(label="Snooze...")
        snooze_custom_btn.set_size_request(90, 40)
        snooze_custom_btn.connect("clicked", self._on_snooze_custom_clicked)
        button_box.pack_start(snooze_custom_btn, False, False, 0)

        main_box.pack_start(button_box, False, False, 0)

        self.add(main_box)

    def _start_elapsed_timer(self):
        """Start updating the elapsed time display."""
        self.elapsed_timeout_id = GLib.timeout_add(1000, self._update_elapsed)

    def _update_elapsed(self):
        """Update elapsed time display."""
        elapsed = datetime.now() - self.completion_time
        total_seconds = int(elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        self.elapsed_label.set_text(f"Elapsed: {hours:02d}:{minutes:02d}:{seconds:02d}")
        return True  # Continue timer

    def _on_stop_clicked(self, button):
        """Handle Stop button click."""
        self._cleanup()
        if self.on_stop_callback:
            self.on_stop_callback(self.timer)
        self.destroy()

    def _on_snooze_clicked(self, button):
        """Handle standard 5-minute snooze."""
        self._do_snooze(self.STANDARD_SNOOZE_MINUTES * 60)

    def _on_snooze_custom_clicked(self, button):
        """Handle custom snooze duration picker."""
        dialog = SnoozeDurationDialog(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            snooze_seconds = dialog.get_snooze_seconds()
            if snooze_seconds > 0:
                self._do_snooze(snooze_seconds)

        dialog.destroy()

    def _do_snooze(self, snooze_seconds):
        """Execute snooze action."""
        self._cleanup()
        if self.on_snooze_callback:
            self.on_snooze_callback(self.timer, snooze_seconds)
        self.destroy()

    def _cleanup(self):
        """Clean up resources."""
        if self.elapsed_timeout_id:
            GLib.source_remove(self.elapsed_timeout_id)
            self.elapsed_timeout_id = None
        if self.sound_player:
            self.sound_player.stop()

    def _on_delete_event(self, widget, event):
        """Prevent window from being closed via window manager."""
        return True  # Block close


class SnoozeDurationDialog(Gtk.Dialog):
    """Dialog for selecting custom snooze duration."""

    def __init__(self, parent):
        """Initialize the snooze duration dialog.

        Args:
            parent: Parent window
        """
        super().__init__(
            title="Custom Snooze",
            transient_for=parent,
            flags=Gtk.DialogFlags.MODAL,
            border_width=15
        )

        self.set_default_size(280, 180)

        box = self.get_content_area()
        box.set_spacing(15)

        label = Gtk.Label(label="Snooze for:")
        label.set_halign(Gtk.Align.START)
        box.pack_start(label, False, False, 0)

        # Time input grid
        time_grid = Gtk.Grid()
        time_grid.set_column_spacing(10)
        time_grid.set_row_spacing(10)

        # Hours
        hours_label = Gtk.Label(label="Hours:")
        hours_label.set_halign(Gtk.Align.END)
        time_grid.attach(hours_label, 0, 0, 1, 1)

        self.hours_spin = Gtk.SpinButton()
        self.hours_spin.set_adjustment(Gtk.Adjustment(0, 0, 23, 1, 1, 0))
        self.hours_spin.set_value(0)
        time_grid.attach(self.hours_spin, 1, 0, 1, 1)

        # Minutes
        minutes_label = Gtk.Label(label="Minutes:")
        minutes_label.set_halign(Gtk.Align.END)
        time_grid.attach(minutes_label, 0, 1, 1, 1)

        self.minutes_spin = Gtk.SpinButton()
        self.minutes_spin.set_adjustment(Gtk.Adjustment(5, 0, 59, 1, 5, 0))
        self.minutes_spin.set_value(5)
        time_grid.attach(self.minutes_spin, 1, 1, 1, 1)

        box.pack_start(time_grid, False, False, 0)

        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        snooze_btn = self.add_button("Snooze", Gtk.ResponseType.OK)
        snooze_btn.get_style_context().add_class("suggested-action")

        self.set_default_response(Gtk.ResponseType.OK)
        self.show_all()

    def get_snooze_seconds(self):
        """Get the selected snooze duration in seconds.

        Returns:
            Snooze duration in seconds
        """
        hours = int(self.hours_spin.get_value())
        minutes = int(self.minutes_spin.get_value())
        return hours * 3600 + minutes * 60
