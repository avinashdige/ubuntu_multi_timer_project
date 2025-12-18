import uuid
import threading
from datetime import datetime


class Timer:
    """Represents a single timer with title and duration."""

    def __init__(self, title, total_seconds):
        """Initialize a new timer.

        Args:
            title: Display name for the timer
            total_seconds: Duration in seconds
        """
        self.id = str(uuid.uuid4())
        self.title = title
        self.total_seconds = total_seconds
        self.remaining_seconds = total_seconds
        self.is_active = True
        self.created_at = datetime.now()
        self.thread = None


class TimerManager:
    """Manages a collection of timers with thread-safe operations."""

    def __init__(self):
        """Initialize the timer manager."""
        self.timers = {}
        self.lock = threading.Lock()
        self.notification_handler = None

    def set_notification_handler(self, handler):
        """Set the notification handler for timer completion.

        Args:
            handler: NotificationHandler instance
        """
        self.notification_handler = handler

    def add_timer(self, title, hours, minutes, seconds):
        """Create and start a new timer.

        Args:
            title: Timer display name
            hours: Hours (0-23)
            minutes: Minutes (0-59)
            seconds: Seconds (0-59)

        Returns:
            Timer ID (UUID string)

        Raises:
            ValueError: If duration is less than 1 second
        """
        from timer_app.timer_thread import TimerThread

        total_seconds = hours * 3600 + minutes * 60 + seconds

        if total_seconds < 1:
            raise ValueError("Timer duration must be at least 1 second")

        with self.lock:
            timer = Timer(title, total_seconds)
            thread = TimerThread(timer, self.on_timer_complete)
            timer.thread = thread
            self.timers[timer.id] = timer
            thread.start()

        return timer.id

    def get_all_timers(self):
        """Get list of all active timers.

        Returns:
            List of Timer objects
        """
        with self.lock:
            return list(self.timers.values())

    def get_timer(self, timer_id):
        """Get a specific timer by ID.

        Args:
            timer_id: UUID string

        Returns:
            Timer object or None if not found
        """
        with self.lock:
            return self.timers.get(timer_id)

    def delete_timer(self, timer_id):
        """Stop and remove a timer.

        Args:
            timer_id: UUID string
        """
        with self.lock:
            if timer_id in self.timers:
                timer = self.timers[timer_id]
                if timer.thread:
                    timer.thread.stop()
                del self.timers[timer_id]

    def on_timer_complete(self, timer):
        """Callback when a timer reaches zero.

        This is called from the main GTK thread via GLib.idle_add.

        Args:
            timer: The completed Timer object
        """
        if self.notification_handler:
            self.notification_handler.notify_timer_complete(timer)
        self.delete_timer(timer.id)

    def shutdown(self):
        """Gracefully shut down all timers."""
        with self.lock:
            for timer in self.timers.values():
                if timer.thread:
                    timer.thread.stop()

            for timer in self.timers.values():
                if timer.thread:
                    timer.thread.join(timeout=2)

            self.timers.clear()
