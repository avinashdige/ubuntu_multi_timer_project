import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from timer_app.utils import validate_timer_input


class AddTimerDialog(Gtk.Dialog):
    """Dialog for creating a new timer."""

    def __init__(self, parent, title_history=None, timer_history=None):
        """Initialize the add timer dialog.

        Args:
            parent: Parent window (can be None)
            title_history: List of previous timer titles for autocomplete
            timer_history: TimerHistory object for duration lookup (preferred)
        """
        super().__init__(
            title="Add New Timer",
            transient_for=parent,
            flags=Gtk.DialogFlags.MODAL,
            border_width=10
        )

        self.set_default_size(350, 200)

        self.timer_data = None
        self.timer_history = timer_history

        box = self.get_content_area()
        box.set_spacing(10)

        title_label = Gtk.Label(label="Timer Title:")
        title_label.set_halign(Gtk.Align.START)
        box.pack_start(title_label, False, False, 0)

        self.title_entry = Gtk.Entry()
        self.title_entry.set_placeholder_text("Enter timer name")
        self.title_entry.set_max_length(50)

        # Set up autocomplete (prefer timer_history object, fallback to title list)
        if timer_history:
            self._setup_autocomplete(timer_history.get_titles())
        elif title_history:
            self._setup_autocomplete(title_history)

        box.pack_start(self.title_entry, False, False, 0)

        duration_label = Gtk.Label(label="Duration:")
        duration_label.set_halign(Gtk.Align.START)
        duration_label.set_margin_top(10)
        box.pack_start(duration_label, False, False, 0)

        time_grid = Gtk.Grid()
        time_grid.set_column_spacing(10)
        time_grid.set_row_spacing(5)

        hours_label = Gtk.Label(label="Hours:")
        hours_label.set_halign(Gtk.Align.END)
        time_grid.attach(hours_label, 0, 0, 1, 1)

        self.hours_spin = Gtk.SpinButton()
        self.hours_spin.set_adjustment(Gtk.Adjustment(0, 0, 23, 1, 5, 0))
        self.hours_spin.set_value(0)
        time_grid.attach(self.hours_spin, 1, 0, 1, 1)

        minutes_label = Gtk.Label(label="Minutes:")
        minutes_label.set_halign(Gtk.Align.END)
        time_grid.attach(minutes_label, 0, 1, 1, 1)

        self.minutes_spin = Gtk.SpinButton()
        self.minutes_spin.set_adjustment(Gtk.Adjustment(0, 0, 59, 1, 5, 0))
        self.minutes_spin.set_value(0)
        time_grid.attach(self.minutes_spin, 1, 1, 1, 1)

        seconds_label = Gtk.Label(label="Seconds:")
        seconds_label.set_halign(Gtk.Align.END)
        time_grid.attach(seconds_label, 0, 2, 1, 1)

        self.seconds_spin = Gtk.SpinButton()
        self.seconds_spin.set_adjustment(Gtk.Adjustment(0, 0, 59, 1, 5, 0))
        self.seconds_spin.set_value(0)
        time_grid.attach(self.seconds_spin, 1, 2, 1, 1)

        box.pack_start(time_grid, False, False, 0)

        # Alarm mode checkbox
        alarm_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        alarm_box.set_margin_top(15)

        self.alarm_checkbox = Gtk.CheckButton(label="Alarm mode (persistent popup with snooze)")
        alarm_box.pack_start(self.alarm_checkbox, False, False, 0)

        box.pack_start(alarm_box, False, False, 0)

        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("Start Timer", Gtk.ResponseType.OK)

        self.set_default_response(Gtk.ResponseType.OK)
        self.title_entry.set_activates_default(True)

        self.connect("response", self.on_response)

        self.show_all()

    def _setup_autocomplete(self, title_history):
        """Set up autocomplete for the title entry.

        Args:
            title_history: List of previous timer titles
        """
        # Create a list store for the autocomplete
        liststore = Gtk.ListStore(str)
        for title in title_history:
            liststore.append([title])

        # Create completion
        completion = Gtk.EntryCompletion()
        completion.set_model(liststore)
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        completion.set_popup_completion(True)
        completion.set_minimum_key_length(1)

        # Connect match-selected signal to auto-populate duration
        completion.connect("match-selected", self._on_autocomplete_selected)

        # Attach to entry
        self.title_entry.set_completion(completion)

    def _on_autocomplete_selected(self, completion, model, iter):
        """Handle autocomplete selection to auto-populate duration.

        Args:
            completion: The Gtk.EntryCompletion
            model: The list store model
            iter: Iterator pointing to the selected row

        Returns:
            False to allow default handler to run
        """
        selected_title = model[iter][0]
        if self.timer_history:
            duration = self.timer_history.get_duration_for_title(selected_title)
            if duration:
                self.hours_spin.set_value(duration.get('hours', 0))
                self.minutes_spin.set_value(duration.get('minutes', 0))
                self.seconds_spin.set_value(duration.get('seconds', 0))
        return False

    def on_response(self, dialog, response_id):
        """Handle dialog response.

        Args:
            dialog: This dialog instance
            response_id: Response type (OK or CANCEL)
        """
        if response_id == Gtk.ResponseType.OK:
            title = self.title_entry.get_text().strip()
            hours = int(self.hours_spin.get_value())
            minutes = int(self.minutes_spin.get_value())
            seconds = int(self.seconds_spin.get_value())

            is_valid, error_message = validate_timer_input(title, hours, minutes, seconds)

            if not is_valid:
                self.show_error(error_message)
                self.stop_emission_by_name("response")
            else:
                self.timer_data = {
                    "title": title,
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds,
                    "timer_type": "alarm" if self.alarm_checkbox.get_active() else "timer"
                }

    def show_error(self, message):
        """Show an error message dialog.

        Args:
            message: Error message to display
        """
        error_dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Invalid Input"
        )
        error_dialog.format_secondary_text(message)
        error_dialog.run()
        error_dialog.destroy()

    def get_timer_data(self):
        """Get the timer data entered by the user.

        Returns:
            Dict with keys: title, hours, minutes, seconds (or None if cancelled)
        """
        return self.timer_data
