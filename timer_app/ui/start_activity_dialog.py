import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class StartActivityDialog(Gtk.Dialog):
    """Dialog for starting a new activity/task."""

    def __init__(self, parent, recent_tasks=None):
        """Initialize the dialog.

        Args:
            parent: Parent window
            recent_tasks: List of recent task dicts for autocomplete
        """
        super().__init__(
            title="Start Activity",
            transient_for=parent,
            flags=Gtk.DialogFlags.MODAL,
            border_width=10
        )
        self.set_default_size(300, 150)

        self.task_name = None

        box = self.get_content_area()
        box.set_spacing(10)

        label = Gtk.Label(label="What are you working on?")
        label.set_halign(Gtk.Align.START)
        box.pack_start(label, False, False, 0)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Task Name (e.g. 'Coding', 'Meeting')")
        
        # Setup autocomplete if recent tasks provided
        if recent_tasks:
            completion = Gtk.EntryCompletion()
            liststore = Gtk.ListStore(str)
            for task in recent_tasks:
                liststore.append([task['name']])
            
            completion.set_model(liststore)
            completion.set_text_column(0)
            completion.set_inline_completion(True)
            self.entry.set_completion(completion)

        box.pack_start(self.entry, False, False, 0)

        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("Start", Gtk.ResponseType.OK)

        self.entry.connect("activate", lambda _: self.response(Gtk.ResponseType.OK))
        self.set_default_response(Gtk.ResponseType.OK)

        self.show_all()

    def get_task_name(self):
        """Get the entered task name."""
        return self.entry.get_text().strip()
