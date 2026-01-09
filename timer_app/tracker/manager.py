import threading
import gi
gi.require_version('GLib', '2.0')
from gi.repository import GLib
from datetime import datetime
import os

from timer_app.tracker.db import TrackerDB

class TrackerManager:
    """Manages time tracking sessions and state."""

    def __init__(self, data_dir=None):
        """Initialize the tracker manager.

        Args:
            data_dir: Directory to store the database (default: ./data)
        """
        if data_dir is None:
            # Determine project root
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(current_dir, 'data')
            
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        self.db = TrackerDB(os.path.join(data_dir, 'time_log.db'))
        self.lock = threading.Lock()
        self.state_change_callbacks = []

    def start_task(self, task_name, category=None):
        """Start tracking a task.

        Args:
            task_name: Name of the task
            category: Optional category
        """
        with self.lock:
            self.db.start_session(task_name, category)
        self._notify_state_changed()

    def stop_task(self, session_id):
        """Stop a specific tracking session.

        Args:
            session_id: ID of the session to stop
        """
        with self.lock:
            self.db.stop_session(session_id)
        self._notify_state_changed()

    def rename_task(self, old_name, new_name):
        """Rename a task.
        
        Args:
            old_name: Current name
            new_name: New name
        """
        with self.lock:
            self.db.rename_task(old_name, new_name)
        self._notify_state_changed()

    def delete_task(self, task_name):
        """Delete a task and its history.
        
        Args:
            task_name: Name of task to delete
        """
        with self.lock:
            self.db.delete_task(task_name)
        self._notify_state_changed()

    def set_task_status(self, task_name, status):
        """Set task status (active/inactive/completed)."""
        with self.lock:
            self.db.set_task_status(task_name, status)
        self._notify_state_changed()

    def get_active_sessions(self):
        """Get all currently active sessions with accumulated time.
        
        Returns:
            List of session dicts
        """
        # No lock needed for read-only DB access (SQLite handles concurrency)
        return self.db.get_active_sessions()

    def get_recent_tasks(self, limit=5):
        """Get recently used active tasks.
        
        Returns:
            List of task dicts
        """
        return self.db.get_recent_tasks(limit)
    
    def get_daily_sessions(self, date=None):
        """Get raw sessions for a specific date (for Gantt chart)."""
        return self.db.get_daily_sessions(date)

    def get_daily_summary(self, date=None):
        """Get summary stats for all tasks on a specific date."""
        return self.db.get_daily_summary(date)

    def add_state_change_callback(self, callback):
        """Register a callback for when tracker state changes (start/stop)."""
        if callback not in self.state_change_callbacks:
            self.state_change_callbacks.append(callback)

    def _notify_state_changed(self):
        """Notify all listeners that something changed."""
        for callback in self.state_change_callbacks:
            GLib.idle_add(callback)
