import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango, GLib
from datetime import datetime, timedelta
from timer_app.utils import format_tracker_duration

class DashboardDialog(Gtk.Window):
    """Dashboard window showing daily activity report."""

    def __init__(self, tracker_manager):
        super().__init__(title="Daily Activity Dashboard")
        self.set_default_size(900, 600)
        self.set_border_width(10)
        
        self.tracker = tracker_manager
        self.selected_task = None
        
        # Header with Date
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.date_label = Gtk.Label(label=datetime.now().strftime("%A, %B %d, %Y"))
        self.date_label.set_attributes(Pango.AttrList.from_string("weight=bold scale=1.2"))
        header_box.pack_start(self.date_label, False, False, 0)
        
        # Main content
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.pack_start(header_box, False, False, 0)
        
        # Tabs
        notebook = Gtk.Notebook()
        
        # Tab 1: Timeline (Gantt)
        self.timeline_area = TimelineArea()
        timeline_scroll = Gtk.ScrolledWindow()
        timeline_scroll.add(self.timeline_area)
        notebook.append_page(timeline_scroll, Gtk.Label(label="Timeline"))
        
        # Tab 2: Summary Table
        summary_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        # Toolbar
        toolbar = Gtk.Toolbar()
        summary_vbox.pack_start(toolbar, False, False, 0)
        
        # Edit Button
        self.btn_edit = Gtk.ToolButton(icon_name="document-edit")
        self.btn_edit.set_label("Edit Name")
        self.btn_edit.set_is_important(True)
        self.btn_edit.set_sensitive(False)
        self.btn_edit.connect("clicked", self._on_edit_clicked)
        toolbar.insert(self.btn_edit, -1)
        
        toolbar.insert(Gtk.SeparatorToolItem(), -1)
        
        # Active/Inactive Buttons
        self.btn_active = Gtk.ToolButton(icon_name="media-playback-start")
        self.btn_active.set_label("Mark Active")
        self.btn_active.set_sensitive(False)
        self.btn_active.connect("clicked", lambda _: self._set_status('active'))
        toolbar.insert(self.btn_active, -1)
        
        self.btn_inactive = Gtk.ToolButton(icon_name="media-playback-pause")
        self.btn_inactive.set_label("Mark Inactive")
        self.btn_inactive.set_sensitive(False)
        self.btn_inactive.connect("clicked", lambda _: self._set_status('inactive'))
        toolbar.insert(self.btn_inactive, -1)
        
        # Complete Button
        self.btn_complete = Gtk.ToolButton(icon_name="emblem-ok")
        self.btn_complete.set_label("Mark Complete")
        self.btn_complete.set_sensitive(False)
        self.btn_complete.connect("clicked", lambda _: self._set_status('completed'))
        toolbar.insert(self.btn_complete, -1)
        
        toolbar.insert(Gtk.SeparatorToolItem(), -1)
        
        # Delete Button
        self.btn_delete = Gtk.ToolButton(icon_name="edit-delete")
        self.btn_delete.set_label("Delete")
        self.btn_delete.set_sensitive(False)
        self.btn_delete.connect("clicked", self._on_delete_clicked)
        toolbar.insert(self.btn_delete, -1)

        # Table
        # Columns: Task Name | Status | First Start | Last Pause | Total Time | raw_status
        self.summary_store = Gtk.ListStore(str, str, str, str, str, str)
        self.summary_tree = Gtk.TreeView(model=self.summary_store)
        
        cols = ["Task Name", "Status", "First Start", "Last Pause", "Total Time"]
        for i, title in enumerate(cols):
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, renderer, text=i)
            col.set_sort_column_id(i)
            col.set_resizable(True)
            self.summary_tree.append_column(col)
        
        selection = self.summary_tree.get_selection()
        selection.connect("changed", self._on_selection_changed)
            
        summary_scroll = Gtk.ScrolledWindow()
        summary_scroll.add(self.summary_tree)
        summary_vbox.pack_start(summary_scroll, True, True, 0)
        
        notebook.append_page(summary_vbox, Gtk.Label(label="Summary"))
        
        vbox.pack_start(notebook, True, True, 0)
        self.add(vbox)
        
        self.refresh_data(None)
        
        # Start auto-refresh timer (1 second)
        self.timeout_id = GLib.timeout_add(1000, self._on_timeout)
        self.connect("destroy", self._on_destroy)

    def _on_timeout(self):
        """Called every second to refresh data."""
        self.refresh_data(None)
        return True

    def _on_destroy(self, widget):
        """Cleanup timer on destroy."""
        if self.timeout_id:
            GLib.source_remove(self.timeout_id)
            self.timeout_id = None

    def _on_selection_changed(self, selection):
        """Handle row selection."""
        model, iter_ = selection.get_selected()
        if iter_:
            self.selected_task = model[iter_][0] # Task Name
            status = model[iter_][5] # Raw Status
            
            self.btn_edit.set_sensitive(True)
            self.btn_delete.set_sensitive(True)
            
            # Update status buttons
            self.btn_active.set_sensitive(status != 'active')
            self.btn_inactive.set_sensitive(status != 'inactive')
            self.btn_complete.set_sensitive(status != 'completed')
        else:
            self.selected_task = None
            self.btn_edit.set_sensitive(False)
            self.btn_delete.set_sensitive(False)
            self.btn_active.set_sensitive(False)
            self.btn_inactive.set_sensitive(False)
            self.btn_complete.set_sensitive(False)

    def _on_edit_clicked(self, widget):
        if not self.selected_task: return
        
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=f"Rename '{self.selected_task}'"
        )
        
        entry = Gtk.Entry()
        entry.set_text(self.selected_task)
        dialog.get_content_area().pack_start(entry, True, True, 10)
        dialog.show_all()
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            new_name = entry.get_text().strip()
            if new_name and new_name != self.selected_task:
                self.tracker.rename_task(self.selected_task, new_name)
                # Refresh happens automatically via timeout or callback logic if implemented
                self.refresh_data(None)
        
        dialog.destroy()

    def _on_delete_clicked(self, widget):
        if not self.selected_task: return
        
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=f"Delete '{self.selected_task}'?"
        )
        dialog.format_secondary_text("This will delete the task and ALL historic sessions associated with it. This cannot be undone.")
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.tracker.delete_task(self.selected_task)
            self.refresh_data(None)
            
        dialog.destroy()

    def _set_status(self, status):
        if not self.selected_task: return
        self.tracker.set_task_status(self.selected_task, status)
        self.refresh_data(None)

    def refresh_data(self, widget):
        """Fetch data and redraw."""
        # Check if window is still valid (not destroyed)
        if not self.get_visible():
            return

        # Update Timeline (keep using raw sessions for granular chart)
        # Note: TrackerManager still has get_daily_sessions for this
        raw_sessions = self.tracker.get_daily_sessions()
        self.timeline_area.set_sessions(raw_sessions)
        
        # Update Summary Table using aggregated data
        summary_data = self.tracker.get_daily_summary()
        
        # Preserve selection
        selection = self.summary_tree.get_selection()
        model, iter_ = selection.get_selected()
        selected_name = model[iter_][0] if iter_ else None
        
        self.summary_store.clear()
        
        for task in summary_data:
            name = task['name']
            status = task['status'] if task['status'] else 'active'
            
            # Format times
            start_str = task['first_start'].strftime("%H:%M") if task['first_start'] else "-"
            
            pause_str = "-"
            if task['last_pause']:
                pause_str = task['last_pause'].strftime("%H:%M")
            elif task['is_running']:
                # If running, logic says "show 'last pause time' if they were paused at any moment"
                # But 'last_pause' in DB logic captures the end time of the *last completed session*.
                # If there are prior sessions today, 'last_pause' will be set.
                pass 
            
            total_str = format_tracker_duration(task['total_seconds'])
            
            display_status = status.capitalize()
            if task['is_running']:
                display_status += " (Running)"
            
            self.summary_store.append([
                name,
                display_status,
                start_str,
                pause_str,
                total_str,
                status # Hidden raw status
            ])
            
        # Restore selection
        if selected_name:
            for row in self.summary_store:
                if row[0] == selected_name:
                    self.summary_tree.set_cursor(row.path, None, False)
                    break

class TimelineArea(Gtk.DrawingArea):
    """Custom widget to draw the Gantt chart."""
    
    def __init__(self):
        super().__init__()
        self.sessions = []
        self.set_size_request(800, 300) # Min height and width
        self.connect("draw", self.on_draw)
        
    def set_sessions(self, sessions):
        self.sessions = sessions
        self.queue_draw()
        
    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        
        # Background
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        
        if not self.sessions:
            # Draw "No Data" text
            cr.set_source_rgb(0.5, 0.5, 0.5)
            layout = widget.create_pango_layout("No activity recorded today")
            
            # Center text
            ink_rect, logical_rect = layout.get_pixel_extents()
            text_x = (width - logical_rect.width) / 2
            text_y = (height - logical_rect.height) / 2
            
            cr.move_to(text_x, text_y)
            Pango.cairo_show_layout(cr, layout)
            return

        # Setup Time Axis (00:00 to 24:00)
        # Using today's date for reference
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        seconds_in_day = 86400
        pixels_per_sec = (width - 40) / seconds_in_day # 20px padding left/right
        
        # Draw Hour Markers
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.set_line_width(1)
        for h in range(0, 25):
            x = 20 + (h * 3600 * pixels_per_sec)
            cr.move_to(x, 0)
            cr.line_to(x, height - 20)
            cr.stroke()
            
            # Text (every 2 hours to avoid crowding)
            if h % 2 == 0:
                layout = widget.create_pango_layout(f"{h:02}")
                cr.move_to(x - 5, height - 15)
                cr.set_source_rgb(0.5, 0.5, 0.5)
                Pango.cairo_show_layout(cr, layout)

        # Organize overlapping tasks into "Lanes"
        lanes = [] 
        
        for s in self.sessions:
            start_offset = (s['start_time'] - start_of_day).total_seconds()
            end_time = s['end_time'] if s['end_time'] else datetime.now()
            end_offset = (end_time - start_of_day).total_seconds()
            
            # Skip if out of bounds (e.g. yesterday) - though DB query handles this mostly
            if end_offset < 0 or start_offset > seconds_in_day:
                continue

            # Find a lane
            assigned_lane = -1
            for i, lane in enumerate(lanes):
                overlap = False
                for placed_s in lane:
                    p_start = (placed_s['start_time'] - start_of_day).total_seconds()
                    p_end_time = placed_s['end_time'] if placed_s['end_time'] else datetime.now()
                    p_end = (p_end_time - start_of_day).total_seconds()
                    
                    if not (end_offset < p_start or start_offset > p_end):
                        overlap = True
                        break
                if not overlap:
                    assigned_lane = i
                    lane.append(s)
                    break
            
            if assigned_lane == -1:
                lanes.append([s])
                
        # Draw Bars
        BAR_HEIGHT = 20
        LANE_SPACING = 10
        
        for i, lane in enumerate(lanes):
            y = 20 + (i * (BAR_HEIGHT + LANE_SPACING))
            
            for s in lane:
                start_offset = max(0, (s['start_time'] - start_of_day).total_seconds())
                end_time = s['end_time'] if s['end_time'] else datetime.now()
                end_offset = min(seconds_in_day, (end_time - start_of_day).total_seconds())
                
                bar_width = max(2, (end_offset - start_offset) * pixels_per_sec)
                x = 20 + (start_offset * pixels_per_sec)
                
                # Bar Color
                import hashlib
                h = int(hashlib.md5(s['task_name'].encode()).hexdigest(), 16)
                r = ((h >> 16) & 255) / 255.0
                g = ((h >> 8) & 255) / 255.0
                b = (h & 255) / 255.0
                
                cr.set_source_rgb(r*0.8, g*0.8, b*0.8)
                cr.rectangle(x, y, bar_width, BAR_HEIGHT)
                cr.fill()
                
                # Border
                cr.set_source_rgb(r*0.6, g*0.6, b*0.6)
                cr.set_line_width(1)
                cr.rectangle(x, y, bar_width, BAR_HEIGHT)
                cr.stroke()
                
                # Label
                if bar_width > 20:
                    cr.set_source_rgb(1, 1, 1) # White text
                    # Contrast check? Assume dark colors for now
                    
                    layout = widget.create_pango_layout(s['task_name'])
                    layout.set_width(int(bar_width * Pango.SCALE))
                    layout.set_ellipsize(Pango.EllipsizeMode.END)
                    
                    cr.move_to(x + 2, y + 2)
                    Pango.cairo_show_layout(cr, layout)
