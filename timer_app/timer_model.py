import uuid
import threading
from datetime import datetime
import gi
gi.require_version('GLib', '2.0')
from gi.repository import GLib


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
        self.pinned_timer_id = None  # Currently pinned timer ID
        self.pin_change_callbacks = []  # Callbacks for pin changes

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

        should_notify = False
        timer_id = None

        with self.lock:
            timer = Timer(title, total_seconds)
            thread = TimerThread(timer, self.on_timer_complete)
            timer.thread = thread
            self.timers[timer.id] = timer
            timer_id = timer.id
            thread.start()

            # Auto-pin if this is the first timer OR if it finishes sooner than current pin
            if len(self.timers) == 1:
                # First timer - auto-pin it
                self.pinned_timer_id = timer.id
                should_notify = True
            elif self.pinned_timer_id:
                # Check if new timer should become the pinned one
                pinned = self.timers.get(self.pinned_timer_id)
                if pinned and timer.remaining_seconds < pinned.remaining_seconds:
                    self.pinned_timer_id = timer.id
                    should_notify = True

        # Notify outside of lock to avoid deadlock
        if should_notify:
            self._notify_pin_changed()

        return timer_id

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

    def set_pinned_timer(self, timer_id):
        """Pin a specific timer.

        Args:
            timer_id: UUID string of timer to pin, or None to unpin

        Returns:
            bool: True if successful, False if timer_id doesn't exist
        """
        should_notify = False

        with self.lock:
            if timer_id is None:
                # Unpin current timer - will auto-pin earliest
                self.pinned_timer_id = None
                self._auto_pin_earliest()
                should_notify = True
            elif timer_id in self.timers:
                self.pinned_timer_id = timer_id
                should_notify = True
            else:
                return False

        # Notify outside of lock to avoid deadlock
        if should_notify:
            self._notify_pin_changed()

        return True

    def get_pinned_timer(self):
        """Get the currently pinned timer object.

        Returns:
            Timer object or None if no timer is pinned
        """
        with self.lock:
            if self.pinned_timer_id and self.pinned_timer_id in self.timers:
                return self.timers[self.pinned_timer_id]
            return None

    def get_pinned_timer_id(self):
        """Get the ID of the currently pinned timer.

        Returns:
            String timer ID or None
        """
        with self.lock:
            return self.pinned_timer_id

    def unpin_timer(self):
        """Unpin the current timer and auto-pin the earliest timer.

        This is equivalent to set_pinned_timer(None).
        """
        self.set_pinned_timer(None)

    def get_earliest_timer(self):
        """Find the timer that will complete soonest.

        Returns:
            Timer object or None if no timers exist
        """
        with self.lock:
            return self._get_earliest_timer_unlocked()

    def _get_earliest_timer_unlocked(self):
        """Internal helper to find earliest timer without acquiring lock.

        Should only be called within a lock context.

        Returns:
            Timer object or None if no timers exist
        """
        if not self.timers:
            return None

        # Sort by remaining_seconds (ascending), then by created_at for determinism
        return min(
            self.timers.values(),
            key=lambda t: (t.remaining_seconds, t.created_at)
        )

    def add_pin_change_callback(self, callback):
        """Register a callback to be called when the pinned timer changes.

        Args:
            callback: Function that takes no arguments
        """
        with self.lock:
            if callback not in self.pin_change_callbacks:
                self.pin_change_callbacks.append(callback)

    def _auto_pin_earliest(self):
        """Internal method to automatically pin the earliest timer.

        Should only be called within a lock context.
        Does not trigger callbacks - caller is responsible.
        """
        earliest = self._get_earliest_timer_unlocked()
        if earliest:
            self.pinned_timer_id = earliest.id
        else:
            self.pinned_timer_id = None

    def _notify_pin_changed(self):
        """Notify all registered callbacks that the pinned timer changed.

        This method acquires its own lock to copy callbacks, then releases
        it before calling them to avoid deadlock.
        """
        # Copy callbacks while holding lock
        with self.lock:
            callbacks = self.pin_change_callbacks[:]

        # Call callbacks outside of lock to avoid deadlock
        for callback in callbacks:
            GLib.idle_add(callback)

    def delete_timer(self, timer_id):
        """Stop and remove a timer.

        Args:
            timer_id: UUID string
        """
        should_notify = False

        with self.lock:
            if timer_id in self.timers:
                timer = self.timers[timer_id]
                if timer.thread:
                    timer.thread.stop()

                # Check if we're deleting the pinned timer
                was_pinned = (timer_id == self.pinned_timer_id)

                del self.timers[timer_id]

                # If deleted timer was pinned, auto-pin the next earliest
                if was_pinned:
                    self._auto_pin_earliest()
                    should_notify = True

        # Notify outside of lock to avoid deadlock
        if should_notify:
            self._notify_pin_changed()

    def on_timer_complete(self, timer):
        """Callback when a timer reaches zero.

        This is called from the main GTK thread via GLib.idle_add.

        Args:
            timer: The completed Timer object
        """
        should_notify = False
        timer_id = timer.id

        # Check if this timer is pinned
        with self.lock:
            was_pinned = (timer.id == self.pinned_timer_id)

        # Send notification (outside lock to avoid blocking)
        if self.notification_handler:
            self.notification_handler.notify_timer_complete(timer)

        # Delete the timer and update pin
        with self.lock:
            if timer_id in self.timers:
                timer = self.timers[timer_id]
                if timer.thread:
                    timer.thread.stop()
                del self.timers[timer_id]

                # If completed timer was pinned, auto-pin next earliest
                if was_pinned:
                    self._auto_pin_earliest()
                    should_notify = True

        # Notify outside of lock to avoid deadlock
        if should_notify:
            self._notify_pin_changed()

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
